from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiTestsIdHistoryResponse200Page")


@_attrs_define
class GetApiTestsIdHistoryResponse200Page:
    """
    Attributes:
        limit (int):
        offset (int):
        total (int):
    """

    limit: int
    offset: int
    total: int

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        total = self.total

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        total = d.pop("total")

        get_api_tests_id_history_response_200_page = cls(
            limit=limit,
            offset=offset,
            total=total,
        )

        return get_api_tests_id_history_response_200_page
