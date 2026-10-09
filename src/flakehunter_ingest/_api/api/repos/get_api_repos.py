from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_repos_response_200 import GetApiReposResponse200
from ...models.get_api_repos_response_400 import GetApiReposResponse400
from ...models.get_api_repos_response_401 import GetApiReposResponse401
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/repos",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401 | None:
    if response.status_code == 200:
        response_200 = GetApiReposResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetApiReposResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = GetApiReposResponse401.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401]:
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
) -> Response[GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401]:
    """List repositories

     Paginated, ordered by full name. Use it to find a repository's numeric id.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
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
) -> GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401 | None:
    """List repositories

     Paginated, ordered by full name. Use it to find a repository's numeric id.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401]:
    """List repositories

     Paginated, ordered by full name. Use it to find a repository's numeric id.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401 | None:
    """List repositories

     Paginated, ordered by full name. Use it to find a repository's numeric id.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiReposResponse200 | GetApiReposResponse400 | GetApiReposResponse401
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
