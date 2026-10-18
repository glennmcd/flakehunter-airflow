from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_reports_response_413_error import (
        PostApiReportsResponse413Error,
    )


T = TypeVar("T", bound="PostApiReportsResponse413")


@_attrs_define
class PostApiReportsResponse413:
    """
    Attributes:
        error (PostApiReportsResponse413Error):
        request_id (str):
    """

    error: PostApiReportsResponse413Error
    request_id: str

    def to_dict(self) -> dict[str, Any]:
        error = self.error.to_dict()

        request_id = self.request_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
                "requestId": request_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.post_api_reports_response_413_error import (
            PostApiReportsResponse413Error,
        )

        d = dict(src_dict)
        error = PostApiReportsResponse413Error.from_dict(d.pop("error"))

        request_id = d.pop("requestId")

        post_api_reports_response_413 = cls(
            error=error,
            request_id=request_id,
        )

        return post_api_reports_response_413
