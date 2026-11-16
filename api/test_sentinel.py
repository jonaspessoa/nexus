from unittest import TestCase
from unittest.mock import patch

from api.sentinel import check


class SentinelTest(TestCase):
    @patch("api.sentinel.socket.getaddrinfo")
    @patch("api.sentinel.http.client.HTTPSConnection")
    def test_blocks_local_destination(self, connection, resolve):
        resolve.return_value = [(0, 0, 0, "", ("127.0.0.1", 443))]
        self.assertEqual(check("https://example.com"), ("blocked", None, None))
        connection.assert_not_called()

    @patch("api.sentinel.socket.getaddrinfo")
    @patch("api.sentinel.http.client.HTTPSConnection")
    def test_records_redirect_without_following_it(self, connection, resolve):
        resolve.return_value = [(0, 0, 0, "", ("8.8.8.8", 443))]
        client = connection.return_value
        client.getresponse.return_value.status = 302
        self.assertEqual(check("https://example.com/health")[:2], ("up", 302))
        client.request.assert_called_once_with("HEAD", "/health")
        client.close.assert_called_once()
