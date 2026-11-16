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
        with patch("socket.getaddrinfo", resolve):
            return original_connect(fixture_address, timeout, source_address)

    from session import database
    from sqlalchemy import text

    with database().begin() as connection:
        connection.execute(text("UPDATE services SET url = 'http://example.com/health'"))

    try:
        with (
            patch("sentinel.socket.getaddrinfo", return_value=[(0, 0, 0, "", ("8.8.8.8", 80))]),
            patch("sentinel.socket.create_connection", side_effect=connect_to_fixture),
        ):
            for status in (200, 503, 200):
                Fixture.status = status
                run_once()
    finally:
        server.shutdown()

with database().connect() as connection:
    statuses = connection.execute(
        text("SELECT http_status FROM service_checks ORDER BY id DESC LIMIT 3")
    ).scalars().all()
    assert statuses == [200, 503, 200], statuses
