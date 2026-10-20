from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v2_tests_flaky_response_400_error import (
        GetApiV2TestsFlakyResponse400Error,
    )


T = TypeVar("T", bound="GetApiV2TestsFlakyResponse400")


@_attrs_define
class GetApiV2TestsFlakyResponse400:
    """
    Attributes:
        error (GetApiV2TestsFlakyResponse400Error):
        request_id (str):
    """

    error: GetApiV2TestsFlakyResponse400Error
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
        from ..models.get_api_v2_tests_flaky_response_400_error import (
            GetApiV2TestsFlakyResponse400Error,
        )

        d = dict(src_dict)
        error = GetApiV2TestsFlakyResponse400Error.from_dict(d.pop("error"))

        request_id = d.pop("requestId")

        get_api_v2_tests_flaky_response_400 = cls(
            error=error,
            request_id=request_id,
        )

        return get_api_v2_tests_flaky_response_400
