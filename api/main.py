from fastapi import FastAPI

from session import router as session_router

app = FastAPI(title="Nexus")
app.include_router(session_router)


@app.get("/health")
def health():
    return {"status": "ok"}
