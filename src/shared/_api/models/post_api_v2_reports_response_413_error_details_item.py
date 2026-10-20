from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV2ReportsResponse413ErrorDetailsItem")


@_attrs_define
class PostApiV2ReportsResponse413ErrorDetailsItem:
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

        post_api_v2_reports_response_413_error_details_item = cls(
            path=path,
            message=message,
        )

        return post_api_v2_reports_response_413_error_details_item
