import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from session import database, require_operator

router = APIRouter(dependencies=[Depends(require_operator)])


@router.get("/services/{service_id}/checks")
def history(service_id: int):
    with database().connect() as connection:
        service = connection.execute(
            text("SELECT id, name FROM services WHERE id = :id"), {"id": service_id}
        ).mappings().one_or_none()
        if service is None:
            raise HTTPException(404, "Service not found")

        checks = connection.execute(
            text(
                "SELECT id, checked_at, outcome, http_status, latency_ms FROM service_checks "
                "WHERE service_id = :id ORDER BY checked_at DESC, id DESC LIMIT 20"
            ),
            {"id": service_id},
        ).mappings()
        results = [dict(row) for row in checks]
        interval = int(os.getenv("NEXUS_CHECK_INTERVAL_SECONDS", "300"))
        stale = bool(results) and (
            datetime.now(timezone.utc) - results[0]["checked_at"]
        ).total_seconds() > 2 * interval
        return {"service": dict(service), "checks": results, "stale": stale}
