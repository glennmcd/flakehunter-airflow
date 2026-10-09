from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.post_api_reports_response_401_error import (
        PostApiReportsResponse401Error,
    )


T = TypeVar("T", bound="PostApiReportsResponse401")


@_attrs_define
class PostApiReportsResponse401:
    """
    Attributes:
        error (PostApiReportsResponse401Error):
        request_id (str):
    """

    error: PostApiReportsResponse401Error
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
        from ..models.post_api_reports_response_401_error import (
            PostApiReportsResponse401Error,
        )

        d = dict(src_dict)
        error = PostApiReportsResponse401Error.from_dict(d.pop("error"))

        request_id = d.pop("requestId")

        post_api_reports_response_401 = cls(
            error=error,
            request_id=request_id,
        )

        return post_api_reports_response_401
