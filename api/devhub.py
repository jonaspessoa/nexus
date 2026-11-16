"""Fetch the latest activity for one GitHub repository."""

import json
import re
from urllib.request import Request, urlopen


def recent_activity(repository: str) -> list[dict]:
    if not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Use owner/name")
    if repository.split("/")[1] in {".", ".."}:
        raise ValueError("Use owner/name")

    request = Request(
        f"https://api.github.com/repos/{repository}/issues?state=all&sort=updated&per_page=30",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "Nexus-DevHub"},
    )
    with urlopen(request, timeout=10) as response:
        payload = json.load(response)

    activity = []
    for item in payload:
        is_pr = "pull_request" in item
        path = "pull" if is_pr else "issues"
        number = item["number"]
        activity.append({
            "number": number,
            "kind": "pull_request" if is_pr else "issue",
            "title": item["title"],
            "state": item["state"],
            "updated_at": item["updated_at"],
            "url": f"https://github.com/{repository}/{path}/{number}",
        })
    return activity
