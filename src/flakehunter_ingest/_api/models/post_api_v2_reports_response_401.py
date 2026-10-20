from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v2_reports_response_401_error import (
        PostApiV2ReportsResponse401Error,
    )


T = TypeVar("T", bound="PostApiV2ReportsResponse401")


@_attrs_define
class PostApiV2ReportsResponse401:
    """
    Attributes:
        error (PostApiV2ReportsResponse401Error):
        request_id (str):
    """

    error: PostApiV2ReportsResponse401Error
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
        from ..models.post_api_v2_reports_response_401_error import (
            PostApiV2ReportsResponse401Error,
        )

        d = dict(src_dict)
        error = PostApiV2ReportsResponse401Error.from_dict(d.pop("error"))

        request_id = d.pop("requestId")

        post_api_v2_reports_response_401 = cls(
            error=error,
            request_id=request_id,
        )

        return post_api_v2_reports_response_401
