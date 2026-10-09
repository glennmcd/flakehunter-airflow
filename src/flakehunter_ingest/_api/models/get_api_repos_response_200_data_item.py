from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="GetApiReposResponse200DataItem")


@_attrs_define
class GetApiReposResponse200DataItem:
    """
    Attributes:
        id (int):
        full_name (str):
        owner (str):
        name (str):
    """

    id: int
    full_name: str
    owner: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        full_name = self.full_name

        owner = self.owner

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "fullName": full_name,
                "owner": owner,
                "name": name,
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

        get_api_repos_response_200_data_item = cls(
            id=id,
            full_name=full_name,
            owner=owner,
            name=name,
        )

        return get_api_repos_response_200_data_item
