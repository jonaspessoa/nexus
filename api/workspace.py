from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, StringConstraints
from sqlalchemy import text

from session import database, require_operator

router = APIRouter(dependencies=[Depends(require_operator)])
TaskStatus = Literal["todo", "in_progress", "done"]


class NewTask(BaseModel):
    project_id: int
    service_id: int | None = None
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class TaskUpdate(BaseModel):
    status: TaskStatus


@router.get("/workspace")
def workspace():
    with database().connect() as connection:
        projects = connection.execute(text("SELECT id, name FROM projects ORDER BY name, id"))
        services = connection.execute(
            text("SELECT id, project_id, name, url FROM services ORDER BY name, id")
        )
        tasks = connection.execute(
            text("SELECT id, project_id, service_id, title, status FROM tasks ORDER BY id")
        )
        return {
            "projects": [dict(row) for row in projects.mappings()],
            "services": [dict(row) for row in services.mappings()],
            "tasks": [dict(row) for row in tasks.mappings()],
        }


@router.post("/tasks", status_code=201)
def create_task(body: NewTask):
    with database().begin() as connection:
        row = connection.execute(
            text(
                "INSERT INTO tasks (project_id, service_id, title) "
                "SELECT p.id, :service_id, :title FROM projects AS p "
                "WHERE p.id = :project_id AND (CAST(:service_id AS integer) IS NULL OR EXISTS ("
                "SELECT 1 FROM services AS s WHERE s.id = :service_id AND s.project_id = p.id)) "
                "RETURNING id, project_id, service_id, title, status"
            ),
            body.model_dump(),
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(404, "Project or service not found")
        return dict(row)


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    with database().begin() as connection:
        row = connection.execute(
            text(
                "UPDATE tasks SET status = :status WHERE id = :id "
                "RETURNING id, project_id, service_id, title, status"
            ),
            {"id": task_id, "status": body.status},
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(404, "Task not found")
        return dict(row)
