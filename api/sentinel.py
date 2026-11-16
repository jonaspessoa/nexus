"""Check a public HTTP endpoint without following redirects."""

import http.client
import ipaddress
import socket
from time import monotonic
from urllib.parse import urlsplit


def check(url):
    started = monotonic()
    try:
        target = urlsplit(url)
        if (
            target.scheme not in {"http", "https"}
            or not target.hostname
            or target.username is not None
            or target.port not in {None, {"http": 80, "https": 443}[target.scheme]}
        ):
            return "blocked", None, None

        port = 443 if target.scheme == "https" else 80
        addresses = socket.getaddrinfo(target.hostname, port, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            return "blocked", None, None

        address = addresses[0][4][0]
        connection_type = (
            http.client.HTTPSConnection if target.scheme == "https" else http.client.HTTPConnection
        )
        connection = connection_type(target.hostname, port, timeout=5)
        # Keep the original hostname for Host and TLS, but connect to the validated address.
        connection._create_connection = lambda _, timeout, source: socket.create_connection(
            (address, port), timeout, source
        )
        try:
            path = target.path or "/"
            if target.query:
                path += "?" + target.query
            connection.request("HEAD", path)
            status = connection.getresponse().status
        finally:
            connection.close()
    except ValueError:
        return "blocked", None, None
    except (OSError, http.client.HTTPException):
        return "down", None, round((monotonic() - started) * 1000)

    if not 100 <= status <= 599:
        return "down", None, round((monotonic() - started) * 1000)
    return ("up" if 200 <= status < 400 else "down"), status, round((monotonic() - started) * 1000)
