FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py session.py workspace.py devhub.py github_routes.py sentinel_routes.py sentinel.py check_worker.py seed.py alembic.ini .
COPY migrations ./migrations
USER 10001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
