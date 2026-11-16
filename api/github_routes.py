import json
import os
from urllib.error import URLError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from devhub import recent_activity
from session import database, require_operator

router = APIRouter(prefix="/devhub", dependencies=[Depends(require_operator)])


@router.get("")
def activity():
    repository = os.getenv("NEXUS_GITHUB_REPOSITORY", "").strip().lower()
    if not repository:
        return {"repository": None, "items": [], "synced_at": None}
    with database().connect() as connection:
        snapshot = connection.execute(
            text("SELECT items, synced_at FROM github_activity WHERE repository = :repository"),
            {"repository": repository},
        ).mappings().one_or_none()
    return {"repository": repository, **(snapshot or {"items": [], "synced_at": None})}


@router.post("/sync")
def sync():
    repository = os.getenv("NEXUS_GITHUB_REPOSITORY", "").strip().lower()
    if not repository:
        raise HTTPException(409, "Set NEXUS_GITHUB_REPOSITORY")
    try:
        items = recent_activity(repository)
    except (URLError, TimeoutError, ValueError, KeyError, TypeError):
        raise HTTPException(502, "GitHub activity could not be refreshed") from None

    with database().begin() as connection:
        synced_at = connection.execute(
            text(
                "INSERT INTO github_activity (repository, items, synced_at) "
                "VALUES (:repository, CAST(:items AS jsonb), now()) "
                "ON CONFLICT (repository) DO UPDATE "
                "SET items = EXCLUDED.items, synced_at = EXCLUDED.synced_at "
                "RETURNING synced_at"
            ),
            {"repository": repository, "items": json.dumps(items)},
        ).scalar_one()
    return {"repository": repository, "items": items, "synced_at": synced_at}
