import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v2_tests_id_history_response_200 import (
    GetApiV2TestsIdHistoryResponse200,
)
from ...models.get_api_v2_tests_id_history_response_400 import (
    GetApiV2TestsIdHistoryResponse400,
)
from ...models.get_api_v2_tests_id_history_response_401 import (
    GetApiV2TestsIdHistoryResponse401,
)
from ...models.get_api_v2_tests_id_history_response_404 import (
    GetApiV2TestsIdHistoryResponse404,
)
from ...models.get_api_v2_tests_id_history_status import GetApiV2TestsIdHistoryStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    since: datetime.datetime | Unset = UNSET,
    status: GetApiV2TestsIdHistoryStatus | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/tests/{id}/history".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
    | None
):
    if response.status_code == 200:
        response_200 = GetApiV2TestsIdHistoryResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetApiV2TestsIdHistoryResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = GetApiV2TestsIdHistoryResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = GetApiV2TestsIdHistoryResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
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
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    since: datetime.datetime | Unset = UNSET,
    status: GetApiV2TestsIdHistoryStatus | Unset = UNSET,
) -> Response[
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
]:
    """Get a test's history

     Results for one test, newest first. Never includes failure stack traces.

    Args:
        id (int):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        since (datetime.datetime | Unset):
        status (GetApiV2TestsIdHistoryStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV2TestsIdHistoryResponse200 | GetApiV2TestsIdHistoryResponse400 | GetApiV2TestsIdHistoryResponse401 | GetApiV2TestsIdHistoryResponse404]
    """

    kwargs = _get_kwargs(
        id=id,
        limit=limit,
        offset=offset,
        since=since,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    since: datetime.datetime | Unset = UNSET,
    status: GetApiV2TestsIdHistoryStatus | Unset = UNSET,
) -> (
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
    | None
):
    """Get a test's history

     Results for one test, newest first. Never includes failure stack traces.

    Args:
        id (int):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        since (datetime.datetime | Unset):
        status (GetApiV2TestsIdHistoryStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV2TestsIdHistoryResponse200 | GetApiV2TestsIdHistoryResponse400 | GetApiV2TestsIdHistoryResponse401 | GetApiV2TestsIdHistoryResponse404
    """

    return sync_detailed(
        id=id,
        client=client,
        limit=limit,
        offset=offset,
        since=since,
        status=status,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    since: datetime.datetime | Unset = UNSET,
    status: GetApiV2TestsIdHistoryStatus | Unset = UNSET,
) -> Response[
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
]:
    """Get a test's history

     Results for one test, newest first. Never includes failure stack traces.

    Args:
        id (int):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        since (datetime.datetime | Unset):
        status (GetApiV2TestsIdHistoryStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV2TestsIdHistoryResponse200 | GetApiV2TestsIdHistoryResponse400 | GetApiV2TestsIdHistoryResponse401 | GetApiV2TestsIdHistoryResponse404]
    """

    kwargs = _get_kwargs(
        id=id,
        limit=limit,
        offset=offset,
        since=since,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    since: datetime.datetime | Unset = UNSET,
    status: GetApiV2TestsIdHistoryStatus | Unset = UNSET,
) -> (
    GetApiV2TestsIdHistoryResponse200
    | GetApiV2TestsIdHistoryResponse400
    | GetApiV2TestsIdHistoryResponse401
    | GetApiV2TestsIdHistoryResponse404
    | None
):
    """Get a test's history

     Results for one test, newest first. Never includes failure stack traces.

    Args:
        id (int):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        since (datetime.datetime | Unset):
        status (GetApiV2TestsIdHistoryStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV2TestsIdHistoryResponse200 | GetApiV2TestsIdHistoryResponse400 | GetApiV2TestsIdHistoryResponse401 | GetApiV2TestsIdHistoryResponse404
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            limit=limit,
            offset=offset,
            since=since,
            status=status,
        )
    ).parsed
