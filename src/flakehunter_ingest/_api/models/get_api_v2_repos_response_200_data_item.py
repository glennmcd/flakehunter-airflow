from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

from ..models.get_api_v2_repos_response_200_data_item_host import (
    GetApiV2ReposResponse200DataItemHost,
)

T = TypeVar("T", bound="GetApiV2ReposResponse200DataItem")


@_attrs_define
class GetApiV2ReposResponse200DataItem:
    """
    Attributes:
        id (int):
        full_name (str):
        owner (str):
        name (str):
        host (GetApiV2ReposResponse200DataItemHost):
    """

    id: int
    full_name: str
    owner: str
    name: str
    host: GetApiV2ReposResponse200DataItemHost

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        full_name = self.full_name

        owner = self.owner

        name = self.name

        host = self.host.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "fullName": full_name,
                "owner": owner,
                "name": name,
                "host": host,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        full_name = d.pop("fullName")

        owner = d.pop("owner")

        name = d.pop("name")

        host = GetApiV2ReposResponse200DataItemHost(d.pop("host"))

        get_api_v2_repos_response_200_data_item = cls(
            id=id,
            full_name=full_name,
            owner=owner,
            name=name,
            host=host,
        )

        return get_api_v2_repos_response_200_data_item
