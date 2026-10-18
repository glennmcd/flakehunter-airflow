from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_reports_response_422_error_code import (
    PostApiReportsResponse422ErrorCode,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_reports_response_422_error_details_item import (
        PostApiReportsResponse422ErrorDetailsItem,
    )


T = TypeVar("T", bound="PostApiReportsResponse422Error")


@_attrs_define
class PostApiReportsResponse422Error:
    """
    Attributes:
        code (PostApiReportsResponse422ErrorCode):
        message (str):
        details (list[PostApiReportsResponse422ErrorDetailsItem] | Unset):
    """

    code: PostApiReportsResponse422ErrorCode
    message: str
    details: list[PostApiReportsResponse422ErrorDetailsItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        code = self.code.value

        message = self.message

        details: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = []
            for details_item_data in self.details:
                details_item = details_item_data.to_dict()
                details.append(details_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "code": code,
                "message": message,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.post_api_reports_response_422_error_details_item import (
            PostApiReportsResponse422ErrorDetailsItem,
        )

        d = dict(src_dict)
        code = PostApiReportsResponse422ErrorCode(d.pop("code"))

        message = d.pop("message")

        _details = d.pop("details", UNSET)
        details: list[PostApiReportsResponse422ErrorDetailsItem] | Unset = UNSET
        if _details is not UNSET:
            details = []
            for details_item_data in _details:
                details_item = PostApiReportsResponse422ErrorDetailsItem.from_dict(
                    details_item_data
                )

                details.append(details_item)

        post_api_reports_response_422_error = cls(
            code=code,
            message=message,
            details=details,
        )

        return post_api_reports_response_422_error
