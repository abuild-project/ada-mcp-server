"""Interpret actual HTTP retry instructions before sharing deadlines across channels."""

import io
import json
import os
import urllib.error
from email.utils import formatdate
from http.client import parse_headers
from types import SimpleNamespace

import pytest
import release_updates as updates

NOW = 1700000000
RESET = str(NOW + 3600)
DATE = formatdate(NOW + 120, usegmt=True)
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
    (503, "Retry-After: 60 \r\n", 60),
    (503, "Retry-After: 60\t\r\n", 60),
    (503, "Retry-After: \t 60 \t\r\n", 60),
    (503, "Retry-After: \t 60\r\n", 60),
    (503, f"Retry-After: {DATE}\r\n", 120),
    (503, f"Retry-After: \t {DATE} \t\r\n", 120),
    (403, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET} \t\r\n", 3600),
    (200, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET} \t\r\n", 3600),
    (
        429,
        f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET} \t\r\nRetry-After: 60\r\n",
        3600,
    ),
    (
        429,
        f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW + 60}\r\nRetry-After: 120 \t\r\n",
        120,
    ),
    (
        429,
        f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW + 60} \t\r\nRetry-After: 120 \t\r\n",
        120,
    ),
    (
        503,
        f"X-RateLimit-Remaining: 42\r\nX-RateLimit-Reset: {RESET} \t\r\nRetry-After: 120 \t\r\n",
        120,
    ),
    (503, "Retry-After: invalid \t\r\n", None),
    (403, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW - 1} \t\r\n", None),
    (503, "Retry-After: 6 0 \t\r\n", None),
    (403, f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {NOW} 0 \t\r\n", None),
]


class Response:
    def __init__(self, headers=None, body=None):
        self.headers = headers if headers is not None else {}
        self.body = (
            b'[{"tag_name":"v0.2.0","draft":false,"prerelease":false}]' if body is None else body
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def geturl(self):
        return updates.API_URL

    def read(self, limit):
        assert limit == updates.MAX_FEED + 1
        if isinstance(self.body, Exception):
            raise self.body
        return self.body[:limit]


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
            if len(requests) == 1 and status >= 400:
                raise urllib.error.HTTPError(updates.API_URL, status, "fixture", headers, None)
            return Response(headers) if len(requests) == 1 else Response()

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
        expected = (
            "up_to_date" if status == 200 else "rate_limited" if status in {403, 429} else "offline"
        )
        assert initial["status"] == expected
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


@pytest.mark.parametrize("remaining", ["0", "42", None, "invalid"])
@pytest.mark.parametrize("body_kind", ["valid", "invalid-json", "oversized", "read-failure"])
def test_received_quota_deadline_survives_body_validation_and_manual_retries(
    tmp_path, monkeypatch, remaining, body_kind
):
    raw = f"X-RateLimit-Reset: \t {RESET} \t\r\n"
    if remaining is not None:
        raw += f"X-RateLimit-Remaining: {remaining}\r\n"
    headers = parse_headers(io.BytesIO((raw + "\r\n").encode("ascii")))
    body = None
    if body_kind == "invalid-json":
        body = b"not-json"
    elif body_kind == "oversized":
        body = b"x" * (updates.MAX_FEED + 1)
    elif body_kind == "read-failure":
        body = OSError("controlled response-read failure")
    clock = SimpleNamespace(now=NOW)
    monkeypatch.setattr(updates, "time", SimpleNamespace(time=lambda: clock.now))
    for retry_channel in ["stable", "prerelease"]:
        clock.now = NOW
        requests, fetched = [], []

        def open_request(request, timeout):
            assert request.full_url == updates.API_URL and timeout == 1.5
            requests.append(request)
            return Response(headers, body) if len(requests) == 1 else Response()

        monkeypatch.setattr(
            updates.urllib.request,
            "build_opener",
            lambda *args: SimpleNamespace(open=open_request),
        )

        def fetch():
            result = updates.fetch_feed()
            fetched.append(result)
            return result

        monkeypatch.setattr(updates, "bounded_fetch", fetch)
        cache = tmp_path / retry_channel / "private-cache"
        initial = updates.check_updates("0.2.0", "stable", cache, manual=True)
        assert initial["status"] == ("up_to_date" if body_kind == "valid" else "offline")
        assert initial["check_performed"] is True and len(requests) == 1
        state = json.loads((cache / "stable.json").read_text())
        deadline = NOW + 3600 if remaining == "0" else None
        assert fetched[0].get("retry_until") == state.get("provider_retry_until") == deadline
        if body_kind == "valid":
            assert fetched[0]["status"] == "ok"
            assert fetched[0]["versions"] == ["0.2.0"] and fetched[0]["complete"] is True
        else:
            assert fetched[0]["status"] == "offline" and "versions" not in fetched[0]
        if deadline is not None:
            clock.now = deadline - 1
            for channel in ["stable", "prerelease"]:
                blocked = updates.check_updates("0.2.0", channel, cache, manual=True)
                assert blocked["status"] == "blocked" and blocked["blocked_until"] == deadline
                assert blocked["check_performed"] is False and len(requests) == 1
            clock.now = deadline
        else:
            clock.now = NOW + 1
        fresh = updates.check_updates("0.2.0", retry_channel, cache, manual=True)
        assert fresh["status"] == "up_to_date" and fresh["check_performed"] is True
        assert len(requests) == 2


def test_unexpected_response_url_cannot_supply_a_provider_deadline(monkeypatch):
    headers = parse_headers(
        io.BytesIO(f"X-RateLimit-Remaining: 0\r\nX-RateLimit-Reset: {RESET}\r\n\r\n".encode())
    )
    response = Response(headers)
    monkeypatch.setattr(updates, "time", SimpleNamespace(time=lambda: NOW))
    monkeypatch.setattr(response, "geturl", lambda: "https://example.invalid/releases")
    monkeypatch.setattr(response, "read", lambda *args: pytest.fail("untrusted URL body read"))
    monkeypatch.setattr(
        updates.urllib.request,
        "build_opener",
        lambda *args: SimpleNamespace(open=lambda *args, **kwargs: response),
    )
    assert updates.fetch_feed() == {"status": "offline"}


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("retry", " \t60\t ", NOW + 60),
        ("reset", f" \t{NOW + 60}\t ", NOW + 60),
        ("retry", "60" + " " * 126, NOW + 60),
        ("reset", str(NOW + 60) + " " * 118, NOW + 60),
        ("retry", "60" + " " * 127, None),
        ("reset", str(NOW + 60) + " " * 119, None),
        ("retry", "0000000000060 \t", None),
        ("reset", "000" + str(NOW + 60) + " \t", None),
    ],
)
def test_ows_normalization_preserves_raw_length_and_numeric_bounds(field, value, expected):
    retry, reset = (value, "") if field == "retry" else ("", value)
    assert updates.retry_deadline(retry, reset, NOW) == expected


@pytest.mark.parametrize("suffix", ["\n", "\r", "\v", "\f", "\u00a0"])
def test_non_http_whitespace_is_not_stripped_from_numeric_deadlines(suffix):
    assert updates.retry_deadline("60" + suffix, "", NOW) is None
    assert updates.retry_deadline("", str(NOW + 60) + suffix, NOW) is None
