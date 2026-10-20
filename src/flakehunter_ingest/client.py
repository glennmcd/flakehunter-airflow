"""Thin wrapper over the generated client for POST /api/v2/reports.

The generated code builds the request and parses responses; this module adds what the spec cannot
express: the real application/xml Content-Type, gzip, the local size limit and 429 handling.
Outcomes follow docs/plans/flakehunter-ingest.md ("Responses").
"""

from __future__ import annotations

import gzip
import io
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import httpx

from flakehunter_ingest._api.api.reports import post_api_v2_reports
from flakehunter_ingest._api.client import AuthenticatedClient
from flakehunter_ingest._api.models.post_api_v2_reports_content_encoding import (
    PostApiV2ReportsContentEncoding,
)
from flakehunter_ingest._api.types import UNSET, File
from flakehunter_ingest.limits import MAX_REPORT_BYTES

REPORT_KEY = "webhook-artifact"
MAX_RATE_LIMIT_RETRIES = 3
DEFAULT_RETRY_AFTER_SECONDS = 5.0

Outcome = Literal["stored", "duplicate", "rejected"]


class UploadError(Exception):
    """Transient failure (5xx, unexpected status). Let Airflow retry the task."""


@dataclass(frozen=True)
class RunHeaders:
    """X-FH-* values, all taken from the GitHub workflow_run, never from Airflow."""

    run_id: int
    run_attempt: int
    sha: str
    branch: str
    workflow: str
    timestamp: str  # RFC 3339, from workflow_run.run_started_at


@dataclass(frozen=True)
class UploadResult:
    outcome: Outcome
    status_code: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    request_id: str | None = None

    def __str__(self) -> str:
        return (
            f"UploadResult(outcome={self.outcome} \n status_code={self.status_code} \n"
            f"error_code={self.error_code} \n error_message={self.error_message}, \n"
            f"request_id={self.request_id})"
        )


def make_client(base_url: str, token: str, *, timeout: float = 60.0) -> AuthenticatedClient:
    return AuthenticatedClient(
        base_url=base_url.rstrip("/"), token=token, timeout=httpx.Timeout(timeout)
    )


def upload_report(
    client: AuthenticatedClient,
    xml: bytes,
    headers: RunHeaders,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> UploadResult:
    if len(xml) > MAX_REPORT_BYTES:
        return UploadResult(
            "rejected",
            error_code="too_large_local",
            error_message=f"merged report is {len(xml)} bytes, limit {MAX_REPORT_BYTES}",
        )

    body = gzip.compress(xml)
    kwargs = post_api_v2_reports._get_kwargs(
        body=File(payload=io.BytesIO(body)),
        x_fh_run_id=headers.run_id,
        x_fh_sha=headers.sha,
        x_fh_run_attempt=headers.run_attempt,
        x_fh_branch=headers.branch or UNSET,
        x_fh_workflow=headers.workflow or UNSET,
        x_fh_report_key=REPORT_KEY,
        x_fh_timestamp=headers.timestamp or UNSET,
        content_encoding=PostApiV2ReportsContentEncoding.GZIP,
    )
    kwargs["content"] = body  # the generated code passes the BinaryIO wrapper
    kwargs["headers"]["Content-Type"] = "application/xml"

    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        raw = client.get_httpx_client().request(**kwargs)  # timeouts propagate: task retries
        status = raw.status_code
        if status == 429 and attempt < MAX_RATE_LIMIT_RETRIES:
            sleep(_retry_after(raw))
            continue
        break

    if status == 201:
        return UploadResult("stored", status)
    if status == 200:
        return UploadResult("duplicate", status)
    # Success bodies are not parsed: only the status matters. Error bodies carry code and requestId.
    parsed = (
        post_api_v2_reports._parse_response(client=client, response=raw)
        if status in (400, 401, 413, 422, 429)
        else None
    )
    if status in (400, 401, 413, 422, 429) and parsed is not None:
        error = parsed.error  # type: ignore[union-attr]
        return UploadResult(
            "rejected",
            status,
            error_code=str(error.code),
            error_message=error.message,
            request_id=parsed.request_id,  # type: ignore[union-attr]
        )
    raise UploadError(f"POST /api/v2/reports returned {status}")


def _retry_after(response: httpx.Response) -> float:
    try:
        return max(0.0, float(response.headers.get("retry-after", "")))
    except ValueError:
        return DEFAULT_RETRY_AFTER_SECONDS
