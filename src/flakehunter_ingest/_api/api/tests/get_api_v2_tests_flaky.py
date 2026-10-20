import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v2_tests_flaky_response_200 import GetApiV2TestsFlakyResponse200
from ...models.get_api_v2_tests_flaky_response_400 import GetApiV2TestsFlakyResponse400
from ...models.get_api_v2_tests_flaky_response_401 import GetApiV2TestsFlakyResponse401
from ...models.get_api_v2_tests_flaky_response_404 import GetApiV2TestsFlakyResponse404
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    repo: str,
    since: datetime.datetime | Unset = UNSET,
    min_runs: int | Unset = 5,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["repo"] = repo

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    params["minRuns"] = min_runs

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/tests/flaky",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
    | None
):
    if response.status_code == 200:
        response_200 = GetApiV2TestsFlakyResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetApiV2TestsFlakyResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = GetApiV2TestsFlakyResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = GetApiV2TestsFlakyResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    repo: str,
    since: datetime.datetime | Unset = UNSET,
    min_runs: int | Unset = 5,
) -> Response[
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
]:
    """Rank flaky tests

     Flake rate = flaky SHAs / SHAs run in the window (skipped results ignored). Only tests with at least
    minRuns SHAs and one flaky SHA appear, most flaky first. repo is a numeric id or a path (owner/name,
    group/sub/project), optionally prefixed with its host (github:acme/widgets). A path without a host
    that matches repositories on more than one host is a 400.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        repo (str):
        since (datetime.datetime | Unset):
        min_runs (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV2TestsFlakyResponse200 | GetApiV2TestsFlakyResponse400 | GetApiV2TestsFlakyResponse401 | GetApiV2TestsFlakyResponse404]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        repo=repo,
        since=since,
        min_runs=min_runs,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    repo: str,
    since: datetime.datetime | Unset = UNSET,
    min_runs: int | Unset = 5,
) -> (
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
    | None
):
    """Rank flaky tests

     Flake rate = flaky SHAs / SHAs run in the window (skipped results ignored). Only tests with at least
    minRuns SHAs and one flaky SHA appear, most flaky first. repo is a numeric id or a path (owner/name,
    group/sub/project), optionally prefixed with its host (github:acme/widgets). A path without a host
    that matches repositories on more than one host is a 400.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        repo (str):
        since (datetime.datetime | Unset):
        min_runs (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV2TestsFlakyResponse200 | GetApiV2TestsFlakyResponse400 | GetApiV2TestsFlakyResponse401 | GetApiV2TestsFlakyResponse404
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        repo=repo,
        since=since,
        min_runs=min_runs,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    repo: str,
    since: datetime.datetime | Unset = UNSET,
    min_runs: int | Unset = 5,
) -> Response[
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
]:
    """Rank flaky tests

     Flake rate = flaky SHAs / SHAs run in the window (skipped results ignored). Only tests with at least
    minRuns SHAs and one flaky SHA appear, most flaky first. repo is a numeric id or a path (owner/name,
    group/sub/project), optionally prefixed with its host (github:acme/widgets). A path without a host
    that matches repositories on more than one host is a 400.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        repo (str):
        since (datetime.datetime | Unset):
        min_runs (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV2TestsFlakyResponse200 | GetApiV2TestsFlakyResponse400 | GetApiV2TestsFlakyResponse401 | GetApiV2TestsFlakyResponse404]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        repo=repo,
        since=since,
        min_runs=min_runs,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    repo: str,
    since: datetime.datetime | Unset = UNSET,
    min_runs: int | Unset = 5,
) -> (
    GetApiV2TestsFlakyResponse200
    | GetApiV2TestsFlakyResponse400
    | GetApiV2TestsFlakyResponse401
    | GetApiV2TestsFlakyResponse404
    | None
):
    """Rank flaky tests

     Flake rate = flaky SHAs / SHAs run in the window (skipped results ignored). Only tests with at least
    minRuns SHAs and one flaky SHA appear, most flaky first. repo is a numeric id or a path (owner/name,
    group/sub/project), optionally prefixed with its host (github:acme/widgets). A path without a host
    that matches repositories on more than one host is a 400.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        repo (str):
        since (datetime.datetime | Unset):
        min_runs (int | Unset):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV2TestsFlakyResponse200 | GetApiV2TestsFlakyResponse400 | GetApiV2TestsFlakyResponse401 | GetApiV2TestsFlakyResponse404
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            repo=repo,
            since=since,
            min_runs=min_runs,
        )
    ).parsed
