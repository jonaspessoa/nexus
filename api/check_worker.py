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
            connection.execute(
                text(
                    "INSERT INTO service_checks (service_id, outcome, http_status, latency_ms) "
                    "SELECT id, :outcome, :status, :latency FROM services "
                    "WHERE id = :id AND url = :url"
                ),
                dict(id=service.id, url=service.url, outcome=outcome, status=status, latency=latency),
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
