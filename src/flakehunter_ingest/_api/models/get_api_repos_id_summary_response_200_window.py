from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="GetApiReposIdSummaryResponse200Window")


@_attrs_define
class GetApiReposIdSummaryResponse200Window:
    """
    Attributes:
        since (str):
    """

    since: str

    def to_dict(self) -> dict[str, Any]:
        since = self.since

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "since": since,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        since = d.pop("since")

        get_api_repos_id_summary_response_200_window = cls(
            since=since,
        )

        return get_api_repos_id_summary_response_200_window
