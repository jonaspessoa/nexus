"""Run a round of service checks at the configured interval."""

import logging
import os
import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from sentinel import check
from session import database

logger = logging.getLogger("nexus.sentinel")


def run_once():
    with database().connect() as connection:
        services = connection.execute(text("SELECT id, url FROM services ORDER BY id")).all()

    for service in services:
        outcome, status, latency = check(service.url)
        with database().begin() as connection:
            current = connection.execute(
                text("SELECT id FROM services WHERE id = :id AND url = :url FOR UPDATE"),
                {"id": service.id, "url": service.url},
            ).scalar_one_or_none()
            if current is None:
                continue
            checked_at = connection.execute(
                text(
                    "INSERT INTO service_checks (service_id, outcome, http_status, latency_ms) "
                    "VALUES (:id, :outcome, :status, :latency) RETURNING checked_at"
                ),
                dict(id=service.id, outcome=outcome, status=status, latency=latency),
            ).scalar_one()
            if outcome == "down":
                connection.execute(
                    text(
                        "WITH opened AS ("
                        "INSERT INTO service_incidents (service_id, opened_at) VALUES (:id, :at) "
                        "ON CONFLICT (service_id) WHERE resolved_at IS NULL DO NOTHING "
                        "RETURNING service_id) "
                        "INSERT INTO tasks (project_id, service_id, title) "
                        "SELECT services.project_id, services.id, left(:prefix || services.name, 120) "
                        "FROM opened JOIN services ON services.id = opened.service_id"
                    ),
                    {"id": service.id, "at": checked_at, "prefix": "Investigar: "},
                )
            elif outcome == "up":
                connection.execute(
                    text(
                        "UPDATE service_incidents SET resolved_at = :at "
                        "WHERE service_id = :id AND resolved_at IS NULL"
                    ),
                    {"id": service.id, "at": checked_at},
                )


def main():
    logging.basicConfig(level=logging.INFO)
    interval = int(os.getenv("NEXUS_CHECK_INTERVAL_SECONDS", "300"))
    if interval < 30:
        raise ValueError("Check interval must be at least 30 seconds")
    while True:
        try:
            run_once()
        except SQLAlchemyError:
            logger.error("Could not save this round of checks. Retrying at the next interval.")
        time.sleep(interval)


if __name__ == "__main__":
    main()
