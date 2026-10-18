from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiTestsIdHistoryResponse400ErrorDetailsItem")


@_attrs_define
class GetApiTestsIdHistoryResponse400ErrorDetailsItem:
    """
    Attributes:
        path (str):
        message (str):
    """

    path: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        message = self.message

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "path": path,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        path = d.pop("path")

        message = d.pop("message")

        get_api_tests_id_history_response_400_error_details_item = cls(
            path=path,
            message=message,
        )

        return get_api_tests_id_history_response_400_error_details_item
