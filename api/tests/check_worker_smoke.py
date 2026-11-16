"""Drive the worker against a local HTTP fixture in the Compose smoke test."""

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import patch

from check_worker import run_once


class Fixture(BaseHTTPRequestHandler):
    status = 200

    def do_HEAD(self):
        self.send_response(self.status)
        self.end_headers()


with HTTPServer(("127.0.0.1", 0), Fixture) as server:
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    original_connect = socket.create_connection
    resolve = socket.getaddrinfo
    fixture_address = server.server_address

    def connect_to_fixture(address, timeout, source_address):
        assert address == ("8.8.8.8", 80)
        return original_connect(fixture_address, timeout, source_address)

    def resolve_fixture(host, port, *args, **kwargs):
        if host == "example.com":
            return [(0, 0, 0, "", ("8.8.8.8", 80))]
        return resolve(host, port, *args, **kwargs)

    from session import database
    from sqlalchemy import text

    with database().begin() as connection:
        connection.execute(text("UPDATE services SET url = 'http://example.com/health'"))

    try:
        with (
            patch("sentinel.socket.getaddrinfo", side_effect=resolve_fixture),
            patch("sentinel.socket.create_connection", side_effect=connect_to_fixture),
        ):
            for status in (200, 503, 503, 200):
                Fixture.status = status
                run_once()
    finally:
        server.shutdown()

with database().connect() as connection:
    statuses = connection.execute(
        text("SELECT http_status FROM service_checks ORDER BY id DESC LIMIT 4")
    ).scalars().all()
    assert statuses == [200, 503, 503, 200], statuses

    incident = connection.execute(
        text("SELECT opened_at, resolved_at FROM service_incidents")
    ).one()
    assert incident.resolved_at > incident.opened_at, incident
