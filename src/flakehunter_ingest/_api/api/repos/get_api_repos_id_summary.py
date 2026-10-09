import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_repos_id_summary_response_200 import (
    GetApiReposIdSummaryResponse200,
)
from ...models.get_api_repos_id_summary_response_400 import (
    GetApiReposIdSummaryResponse400,
)
from ...models.get_api_repos_id_summary_response_401 import (
    GetApiReposIdSummaryResponse401,
)
from ...models.get_api_repos_id_summary_response_404 import (
    GetApiReposIdSummaryResponse404,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    since: datetime.datetime | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/repos/{id}/summary".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
    | None
):
    if response.status_code == 200:
        response_200 = GetApiReposIdSummaryResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetApiReposIdSummaryResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = GetApiReposIdSummaryResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = GetApiReposIdSummaryResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    since: datetime.datetime | Unset = UNSET,
) -> Response[
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
]:
    """Summarise a repository

     Windowed totals for a repository. lastRunAt ignores the window.

    Args:
        id (int):
        since (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiReposIdSummaryResponse200 | GetApiReposIdSummaryResponse400 | GetApiReposIdSummaryResponse401 | GetApiReposIdSummaryResponse404]
    """

    kwargs = _get_kwargs(
        id=id,
        since=since,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    since: datetime.datetime | Unset = UNSET,
) -> (
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
    | None
):
    """Summarise a repository

     Windowed totals for a repository. lastRunAt ignores the window.

    Args:
        id (int):
        since (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiReposIdSummaryResponse200 | GetApiReposIdSummaryResponse400 | GetApiReposIdSummaryResponse401 | GetApiReposIdSummaryResponse404
    """

    return sync_detailed(
        id=id,
        client=client,
        since=since,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    since: datetime.datetime | Unset = UNSET,
) -> Response[
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
]:
    """Summarise a repository

     Windowed totals for a repository. lastRunAt ignores the window.

    Args:
        id (int):
        since (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiReposIdSummaryResponse200 | GetApiReposIdSummaryResponse400 | GetApiReposIdSummaryResponse401 | GetApiReposIdSummaryResponse404]
    """

    kwargs = _get_kwargs(
        id=id,
        since=since,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    since: datetime.datetime | Unset = UNSET,
) -> (
    GetApiReposIdSummaryResponse200
    | GetApiReposIdSummaryResponse400
    | GetApiReposIdSummaryResponse401
    | GetApiReposIdSummaryResponse404
    | None
):
    """Summarise a repository

     Windowed totals for a repository. lastRunAt ignores the window.

    Args:
        id (int):
        since (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiReposIdSummaryResponse200 | GetApiReposIdSummaryResponse400 | GetApiReposIdSummaryResponse401 | GetApiReposIdSummaryResponse404
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            since=since,
        )
    ).parsed
