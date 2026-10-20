from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV2ReposIdSummaryResponse200Repo")


@_attrs_define
class GetApiV2ReposIdSummaryResponse200Repo:
    """
    Attributes:
        id (int):
        full_name (str):
    """

    id: int
    full_name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        full_name = self.full_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "fullName": full_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        full_name = d.pop("fullName")

        get_api_v2_repos_id_summary_response_200_repo = cls(
            id=id,
            full_name=full_name,
        )

        return get_api_v2_repos_id_summary_response_200_repo
