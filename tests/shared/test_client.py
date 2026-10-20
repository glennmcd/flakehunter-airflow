import gzip

import httpx
import pytest
import respx

from shared.client import (
    UploadError,
    upload_report,
)
from shared.limits import MAX_REPORT_BYTES
from tests.conftest import BASE

URL = f"{BASE}/api/v2/reports"
XML = b"<testsuite name='s'><testcase name='t'/></testsuite>"
OK_BODY = {
    "run": {"id": 1, "runId": 123, "runAttempt": 2, "sha": "a" * 40, "branch": "main"},
    "duplicate": False,
    "counts": {"total": 1, "passed": 1, "failed": 0, "errored": 0, "skipped": 0},
}


def err(code: str, status: int):
    return httpx.Response(
        status, json={"error": {"code": code, "message": "nope"}, "requestId": "req-1"}
    )


@respx.mock
def test_headers_body_and_auth(client, headers):
    route = respx.post(URL).mock(return_value=httpx.Response(201, json=OK_BODY))
    result = upload_report(client, XML, headers)
    assert result.outcome == "stored"
    req = route.calls.last.request
    assert req.headers["x-fh-run-id"] == "123"
    assert req.headers["x-fh-run-attempt"] == "2"
    assert req.headers["x-fh-sha"] == "a" * 40
    assert req.headers["x-fh-branch"] == "main"
    assert req.headers["x-fh-workflow"] == "CI"
    assert req.headers["x-fh-report-key"] == "webhook-artifact"
    assert req.headers["x-fh-timestamp"] == "2026-10-08T12:00:00Z"
    assert req.headers["content-encoding"] == "gzip"
    assert req.headers["content-type"] == "application/xml"
    assert req.headers["authorization"] == "Bearer upload-token"
    assert gzip.decompress(req.content) == XML


@respx.mock
def test_duplicate(client, headers):
    respx.post(URL).mock(return_value=httpx.Response(200, json={**OK_BODY, "duplicate": True}))
    assert upload_report(client, XML, headers).outcome == "duplicate"


@respx.mock
@pytest.mark.parametrize(
    ("status", "code"),
    [
        (400, "validation_error"),
        (401, "unauthorized"),
        (413, "payload_too_large"),
        (422, "invalid_report"),
    ],
)
def test_rejections_do_not_raise(client, headers, status, code):
    respx.post(URL).mock(return_value=err(code, status))
    result = upload_report(client, XML, headers)
    assert result.outcome == "rejected"
    assert result.status_code == status
    assert result.error_code == code
    assert result.request_id == "req-1"


@respx.mock
def test_429_waits_then_succeeds(client, headers):
    route = respx.post(URL).mock(
        side_effect=[
            httpx.Response(
                429,
                headers={"Retry-After": "7"},
                json={"error": {"code": "rate_limited", "message": "slow"}, "requestId": "r"},
            ),
            httpx.Response(201, json=OK_BODY),
        ]
    )
    sleeps: list[float] = []
    assert upload_report(client, XML, headers, sleep=sleeps.append).outcome == "stored"
    assert sleeps == [7.0]
    assert route.call_count == 2


@respx.mock
def test_429_gives_up_after_three_retries(client, headers):
    route = respx.post(URL).mock(return_value=err("rate_limited", 429))
    sleeps: list[float] = []
    result = upload_report(client, XML, headers, sleep=sleeps.append)
    assert result.outcome == "rejected"
    assert result.status_code == 429
    assert route.call_count == 4
    assert len(sleeps) == 3


@respx.mock
def test_5xx_raises(client, headers):
    respx.post(URL).mock(return_value=httpx.Response(503, text="down"))
    with pytest.raises(UploadError):
        upload_report(client, XML, headers)


@respx.mock
def test_timeout_propagates(client, headers):
    respx.post(URL).mock(side_effect=httpx.ConnectTimeout("t"))
    with pytest.raises(httpx.TimeoutException):
        upload_report(client, XML, headers)


@respx.mock
def test_oversize_rejected_locally(client, headers):
    route = respx.post(URL)
    result = upload_report(client, b"x" * (MAX_REPORT_BYTES + 1), headers)
    assert result.outcome == "rejected"
    assert not route.called
