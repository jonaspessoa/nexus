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
    pull_request_url: Annotated[
        str, StringConstraints(max_length=255, pattern=r"^https://github[.]com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+/pull/[1-9][0-9]*$")
    ] | None = None
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
            text("SELECT id, project_id, service_id, title, status, pull_request_url FROM tasks ORDER BY id")
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
                "INSERT INTO tasks (project_id, service_id, title, pull_request_url) "
                "SELECT p.id, :service_id, :title, :pull_request_url FROM projects AS p "
                "WHERE p.id = :project_id AND (CAST(:service_id AS integer) IS NULL OR EXISTS ("
                "SELECT 1 FROM services AS s WHERE s.id = :service_id AND s.project_id = p.id)) "
                "RETURNING id, project_id, service_id, title, status, pull_request_url"
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
                "RETURNING id, project_id, service_id, title, status, pull_request_url"
            ),
            {"id": task_id, "status": body.status},
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(404, "Task not found")
        return dict(row)


class NewProject(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


@router.post("/projects", status_code=201)
def create_project(body: NewProject):
    from uuid import uuid4

    with database().begin() as connection:
        project = connection.execute(
            text("INSERT INTO projects (slug, name) VALUES (:slug, :name) RETURNING id, name"),
            {"slug": uuid4().hex, "name": body.name},
        ).mappings().one()
        return dict(project)


class NewService(NewProject):
    url: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2048)]


@router.post("/projects/{project_id}/services", status_code=201)
def create_service(project_id: int, body: NewService):
    from urllib.parse import urlsplit

    try:
        target = urlsplit(body.url)
        if target.scheme not in {"http", "https"} or not target.hostname:
            raise ValueError
        if target.username is not None or target.port not in {None, 80 if target.scheme == "http" else 443}:
            raise ValueError
    except ValueError:
        raise HTTPException(422, "Use an HTTP or HTTPS URL on its standard port") from None

    with database().begin() as connection:
        if not connection.execute(text("SELECT 1 FROM projects WHERE id = :id"), {"id": project_id}).scalar():
            raise HTTPException(404, "Project not found")
        service = connection.execute(
            text(
                "INSERT INTO services (project_id, name, url) VALUES (:id, :name, :url) "
                "ON CONFLICT (project_id, url) DO NOTHING RETURNING id, project_id, name, url"
            ),
            {"id": project_id, **body.model_dump()},
        ).mappings().one_or_none()
        if service is None:
            raise HTTPException(409, "Service URL already registered for this project")
        return dict(service)
