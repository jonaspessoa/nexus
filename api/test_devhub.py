from io import BytesIO
from unittest import TestCase
from unittest.mock import patch

from api.devhub import recent_activity


class DevHubTest(TestCase):
    def test_distinguishes_issues_and_pull_requests(self):
        payload = b"""[
          {"number": 1, "title": "Issue", "state": "open", "updated_at": "2026-11-16T00:00:00Z"},
          {"number": 2, "title": "PR", "state": "open", "updated_at": "2026-11-16T00:00:00Z", "pull_request": {}}
        ]"""
        with patch("api.devhub.urlopen", return_value=BytesIO(payload)) as fetch:
            issue, pr = recent_activity("jonaspessoa/nexus")

        self.assertEqual(issue["kind"], "issue")
        self.assertEqual(pr["kind"], "pull_request")
        self.assertEqual(pr["url"], "https://github.com/jonaspessoa/nexus/pull/2")
        self.assertEqual(fetch.call_args.kwargs["timeout"], 10)

    def test_rejects_path_segments(self):
        with self.assertRaises(ValueError):
            recent_activity("jonaspessoa/..")
