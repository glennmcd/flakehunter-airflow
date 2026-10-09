from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_reports_content_encoding import PostApiReportsContentEncoding
from ...models.post_api_reports_response_200 import PostApiReportsResponse200
from ...models.post_api_reports_response_201 import PostApiReportsResponse201
from ...models.post_api_reports_response_400 import PostApiReportsResponse400
from ...models.post_api_reports_response_401 import PostApiReportsResponse401
from ...models.post_api_reports_response_413 import PostApiReportsResponse413
from ...models.post_api_reports_response_422 import PostApiReportsResponse422
from ...models.post_api_reports_response_429 import PostApiReportsResponse429
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    *,
    body: File,
    x_fh_run_id: int,
    x_fh_sha: str,
    x_fh_run_attempt: int | Unset = 1,
    x_fh_branch: str | Unset = UNSET,
    x_fh_workflow: str | Unset = "upload",
    x_fh_report_key: str | Unset = "default",
    x_fh_timestamp: str | Unset = UNSET,
    content_encoding: PostApiReportsContentEncoding | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-fh-run-id"] = str(x_fh_run_id)

    headers["x-fh-sha"] = x_fh_sha

    if not isinstance(x_fh_run_attempt, Unset):
        headers["x-fh-run-attempt"] = str(x_fh_run_attempt)

    if not isinstance(x_fh_branch, Unset):
        headers["x-fh-branch"] = x_fh_branch

    if not isinstance(x_fh_workflow, Unset):
        headers["x-fh-workflow"] = x_fh_workflow

    if not isinstance(x_fh_report_key, Unset):
        headers["x-fh-report-key"] = x_fh_report_key

    if not isinstance(x_fh_timestamp, Unset):
        headers["x-fh-timestamp"] = x_fh_timestamp

    if not isinstance(content_encoding, Unset):
        headers["content-encoding"] = str(content_encoding)

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/reports",
    }

    _kwargs["content"] = body.payload
    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
    | None
):
    if response.status_code == 200:
        response_200 = PostApiReportsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = PostApiReportsResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = PostApiReportsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = PostApiReportsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 413:
        response_413 = PostApiReportsResponse413.from_dict(response.json())

        return response_413

    if response.status_code == 422:
        response_422 = PostApiReportsResponse422.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = PostApiReportsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: File,
    x_fh_run_id: int,
    x_fh_sha: str,
    x_fh_run_attempt: int | Unset = 1,
    x_fh_branch: str | Unset = UNSET,
    x_fh_workflow: str | Unset = "upload",
    x_fh_report_key: str | Unset = "default",
    x_fh_timestamp: str | Unset = UNSET,
    content_encoding: PostApiReportsContentEncoding | Unset = UNSET,
) -> Response[
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
]:
    """Upload a JUnit XML report

     Authenticated with a per-repository upload token (not the read token); the repository comes from the
    token. Idempotent on (run id, attempt, report key): the first upload returns 201, a repeat returns
    200 with the original counts. A SHA that contradicts an existing run is a 400. Unparseable bodies or
    reports with no testsuite are 422 (invalid_report) and store nothing. Rate limited per IP and per
    token (429 with Retry-After).

    Args:
        x_fh_run_id (int):
        x_fh_sha (str):
        x_fh_run_attempt (int | Unset):  Default: 1.
        x_fh_branch (str | Unset):
        x_fh_workflow (str | Unset):  Default: 'upload'.
        x_fh_report_key (str | Unset):  Default: 'default'.
        x_fh_timestamp (str | Unset):
        content_encoding (PostApiReportsContentEncoding | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiReportsResponse200 | PostApiReportsResponse201 | PostApiReportsResponse400 | PostApiReportsResponse401 | PostApiReportsResponse413 | PostApiReportsResponse422 | PostApiReportsResponse429]
    """

    kwargs = _get_kwargs(
        body=body,
        x_fh_run_id=x_fh_run_id,
        x_fh_sha=x_fh_sha,
        x_fh_run_attempt=x_fh_run_attempt,
        x_fh_branch=x_fh_branch,
        x_fh_workflow=x_fh_workflow,
        x_fh_report_key=x_fh_report_key,
        x_fh_timestamp=x_fh_timestamp,
        content_encoding=content_encoding,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: File,
    x_fh_run_id: int,
    x_fh_sha: str,
    x_fh_run_attempt: int | Unset = 1,
    x_fh_branch: str | Unset = UNSET,
    x_fh_workflow: str | Unset = "upload",
    x_fh_report_key: str | Unset = "default",
    x_fh_timestamp: str | Unset = UNSET,
    content_encoding: PostApiReportsContentEncoding | Unset = UNSET,
) -> (
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
    | None
):
    """Upload a JUnit XML report

     Authenticated with a per-repository upload token (not the read token); the repository comes from the
    token. Idempotent on (run id, attempt, report key): the first upload returns 201, a repeat returns
    200 with the original counts. A SHA that contradicts an existing run is a 400. Unparseable bodies or
    reports with no testsuite are 422 (invalid_report) and store nothing. Rate limited per IP and per
    token (429 with Retry-After).

    Args:
        x_fh_run_id (int):
        x_fh_sha (str):
        x_fh_run_attempt (int | Unset):  Default: 1.
        x_fh_branch (str | Unset):
        x_fh_workflow (str | Unset):  Default: 'upload'.
        x_fh_report_key (str | Unset):  Default: 'default'.
        x_fh_timestamp (str | Unset):
        content_encoding (PostApiReportsContentEncoding | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiReportsResponse200 | PostApiReportsResponse201 | PostApiReportsResponse400 | PostApiReportsResponse401 | PostApiReportsResponse413 | PostApiReportsResponse422 | PostApiReportsResponse429
    """

    return sync_detailed(
        client=client,
        body=body,
        x_fh_run_id=x_fh_run_id,
        x_fh_sha=x_fh_sha,
        x_fh_run_attempt=x_fh_run_attempt,
        x_fh_branch=x_fh_branch,
        x_fh_workflow=x_fh_workflow,
        x_fh_report_key=x_fh_report_key,
        x_fh_timestamp=x_fh_timestamp,
        content_encoding=content_encoding,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: File,
    x_fh_run_id: int,
    x_fh_sha: str,
    x_fh_run_attempt: int | Unset = 1,
    x_fh_branch: str | Unset = UNSET,
    x_fh_workflow: str | Unset = "upload",
    x_fh_report_key: str | Unset = "default",
    x_fh_timestamp: str | Unset = UNSET,
    content_encoding: PostApiReportsContentEncoding | Unset = UNSET,
) -> Response[
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
]:
    """Upload a JUnit XML report

     Authenticated with a per-repository upload token (not the read token); the repository comes from the
    token. Idempotent on (run id, attempt, report key): the first upload returns 201, a repeat returns
    200 with the original counts. A SHA that contradicts an existing run is a 400. Unparseable bodies or
    reports with no testsuite are 422 (invalid_report) and store nothing. Rate limited per IP and per
    token (429 with Retry-After).

    Args:
        x_fh_run_id (int):
        x_fh_sha (str):
        x_fh_run_attempt (int | Unset):  Default: 1.
        x_fh_branch (str | Unset):
        x_fh_workflow (str | Unset):  Default: 'upload'.
        x_fh_report_key (str | Unset):  Default: 'default'.
        x_fh_timestamp (str | Unset):
        content_encoding (PostApiReportsContentEncoding | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiReportsResponse200 | PostApiReportsResponse201 | PostApiReportsResponse400 | PostApiReportsResponse401 | PostApiReportsResponse413 | PostApiReportsResponse422 | PostApiReportsResponse429]
    """

    kwargs = _get_kwargs(
        body=body,
        x_fh_run_id=x_fh_run_id,
        x_fh_sha=x_fh_sha,
        x_fh_run_attempt=x_fh_run_attempt,
        x_fh_branch=x_fh_branch,
        x_fh_workflow=x_fh_workflow,
        x_fh_report_key=x_fh_report_key,
        x_fh_timestamp=x_fh_timestamp,
        content_encoding=content_encoding,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: File,
    x_fh_run_id: int,
    x_fh_sha: str,
    x_fh_run_attempt: int | Unset = 1,
    x_fh_branch: str | Unset = UNSET,
    x_fh_workflow: str | Unset = "upload",
    x_fh_report_key: str | Unset = "default",
    x_fh_timestamp: str | Unset = UNSET,
    content_encoding: PostApiReportsContentEncoding | Unset = UNSET,
) -> (
    PostApiReportsResponse200
    | PostApiReportsResponse201
    | PostApiReportsResponse400
    | PostApiReportsResponse401
    | PostApiReportsResponse413
    | PostApiReportsResponse422
    | PostApiReportsResponse429
    | None
):
    """Upload a JUnit XML report

     Authenticated with a per-repository upload token (not the read token); the repository comes from the
    token. Idempotent on (run id, attempt, report key): the first upload returns 201, a repeat returns
    200 with the original counts. A SHA that contradicts an existing run is a 400. Unparseable bodies or
    reports with no testsuite are 422 (invalid_report) and store nothing. Rate limited per IP and per
    token (429 with Retry-After).

    Args:
        x_fh_run_id (int):
        x_fh_sha (str):
        x_fh_run_attempt (int | Unset):  Default: 1.
        x_fh_branch (str | Unset):
        x_fh_workflow (str | Unset):  Default: 'upload'.
        x_fh_report_key (str | Unset):  Default: 'default'.
        x_fh_timestamp (str | Unset):
        content_encoding (PostApiReportsContentEncoding | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiReportsResponse200 | PostApiReportsResponse201 | PostApiReportsResponse400 | PostApiReportsResponse401 | PostApiReportsResponse413 | PostApiReportsResponse422 | PostApiReportsResponse429
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_fh_run_id=x_fh_run_id,
            x_fh_sha=x_fh_sha,
            x_fh_run_attempt=x_fh_run_attempt,
            x_fh_branch=x_fh_branch,
            x_fh_workflow=x_fh_workflow,
            x_fh_report_key=x_fh_report_key,
            x_fh_timestamp=x_fh_timestamp,
            content_encoding=content_encoding,
        )
    ).parsed
