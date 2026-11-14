"""Interpret actual HTTP retry instructions before sharing deadlines across channels."""

import io
import json
import os
import urllib.error
from http.client import parse_headers
from types import SimpleNamespace

import pytest
import release_updates as updates

NOW = 1700000000
RESET = str(NOW + 3600)
CASES = [
    (500, f"X-RateLimit-Remaining: 42\r\nX-RateLimit-Reset: {RESET}\r\n", None),
    (429, f"X-RateLimit-Remaining: 42\r\nX-RateLimit-Reset: {RESET}\r\nRetry-After: 60\r\n", 60),
    (403, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET}\r\n", 3600),
    (429, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET}\r\nRetry-After: 60\r\n", 3600),
    (
        429,
        f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW + 60}\r\nRetry-After: 120\r\n",
        120,
    ),
    (503, "retry-after: 120\r\n", 120),
    (503, f"X-RateLimit-Remaining: 42\r\nX-RateLimit-Reset: {RESET}\r\nRetry-After: 120\r\n", 120),
    (429, f"x-ratelimit-remaining: \t0 \r\nX-rAtElImIt-ReSeT: {RESET}\r\n", 3600),
    (429, f"X-RateLimit-Reset: {RESET}\r\nRetry-After: 60\r\n", 60),
    (
        429,
        f"X-RateLimit-Remaining: invalid\r\nX-RateLimit-Reset: {RESET}\r\nRetry-After: 60\r\n",
        60,
    ),
    (429, f"X-RateLimit-Remaining: -1\r\nX-RateLimit-Reset: {RESET}\r\nRetry-After: 60\r\n", 60),
    (429, "X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: invalid\r\nRetry-After: 60\r\n", 60),
    (
        429,
        f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW - 1}\r\nRetry-After: invalid\r\n",
        None,
    ),
]


class Response:
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def geturl(self):
        return updates.API_URL

    def read(self, limit):
        assert limit == updates.MAX_FEED + 1
        return b'[{"tag_name":"v0.2.0","draft":false,"prerelease":false}]'


@pytest.mark.parametrize("status,raw_headers,delay", CASES)
def test_http_deadlines_and_manual_retries_across_channels(
    tmp_path, monkeypatch, status, raw_headers, delay
):
    # Real HTTPMessage parsing covers case-insensitive names and field whitespace.
    headers = parse_headers(io.BytesIO((raw_headers + "\r\n").encode("ascii")))
    clock = SimpleNamespace(now=NOW)
    monkeypatch.setattr(updates, "time", SimpleNamespace(time=lambda: clock.now))
    for retry_channel in ["stable", "prerelease"]:
        clock.now = NOW
        requests, fetched = [], []

        def open_request(request, timeout):
            assert request.full_url == updates.API_URL and timeout == 1.5
            requests.append(request)
            if len(requests) == 1:
                raise urllib.error.HTTPError(updates.API_URL, status, "fixture", headers, None)
            return Response()

        monkeypatch.setattr(
            updates.urllib.request,
            "build_opener",
            lambda *args: SimpleNamespace(open=open_request),
        )

        def fetch():
            response = updates.fetch_feed()
            fetched.append(response)
            return response

        # Keep the actual HTTP-error/cache logic in one process for the fixture;
        # the isolated child and its total timeout have separate controls.
        monkeypatch.setattr(updates, "bounded_fetch", fetch)
        cache = tmp_path / retry_channel / "private-cache"
        initial = updates.check_updates("0.2.0", "stable", cache, manual=True)
        assert initial["status"] == ("rate_limited" if status in {403, 429} else "offline")
        assert initial["check_performed"] is True and len(requests) == 1
        state = json.loads((cache / "stable.json").read_text())
        deadline = None if delay is None else NOW + delay
        assert fetched[0].get("retry_until") == deadline
        assert state.get("provider_retry_until") == deadline
        assert state["next_check_at"] == NOW + updates.DAY
        if delay is not None:
            clock.now = NOW + delay - 1
            for channel in ["stable", "prerelease"]:
                blocked = updates.check_updates("0.2.0", channel, cache, manual=True)
                assert blocked["status"] == "blocked"
                assert blocked["blocked_until"] == deadline
                assert blocked["check_performed"] is False and len(requests) == 1
            clock.now = NOW + delay
        else:
            clock.now = NOW + 1
        # Explicit fresh checks bypass the daily/offline cooldown as soon as
        # there is no actual provider deadline, on either channel independently.
        retried = updates.check_updates("0.2.0", retry_channel, cache, manual=True)
        assert retried["status"] == "up_to_date" and retried["check_performed"] is True
        assert len(requests) == 2 and fetched[-1]["status"] == "ok"
        assert os.environ["ADA_MCP_UPDATE_CHANNEL"] == "off"
