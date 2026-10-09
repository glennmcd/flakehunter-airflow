from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="GetApiReposIdSummaryResponse200Repo")


@_attrs_define
class GetApiReposIdSummaryResponse200Repo:
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

        get_api_repos_id_summary_response_200_repo = cls(
            id=id,
            full_name=full_name,
        )

        return get_api_repos_id_summary_response_200_repo
