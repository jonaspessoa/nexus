from fastapi import FastAPI

from github_routes import router as github_router
from sentinel_routes import router as sentinel_router
from session import router as session_router
from workspace import router as workspace_router

app = FastAPI(title="Nexus")
app.include_router(session_router)
app.include_router(workspace_router)
app.include_router(github_router)
app.include_router(sentinel_router)


@app.get("/health")
def health():
    return {"status": "ok"}
