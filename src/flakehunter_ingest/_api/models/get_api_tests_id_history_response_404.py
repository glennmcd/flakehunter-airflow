from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_tests_id_history_response_404_error import (
        GetApiTestsIdHistoryResponse404Error,
    )


T = TypeVar("T", bound="GetApiTestsIdHistoryResponse404")


@_attrs_define
class GetApiTestsIdHistoryResponse404:
    """
    Attributes:
        error (GetApiTestsIdHistoryResponse404Error):
        request_id (str):
    """

    error: GetApiTestsIdHistoryResponse404Error
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
        from ..models.get_api_tests_id_history_response_404_error import (
            GetApiTestsIdHistoryResponse404Error,
        )

        d = dict(src_dict)
        error = GetApiTestsIdHistoryResponse404Error.from_dict(d.pop("error"))

        request_id = d.pop("requestId")

        get_api_tests_id_history_response_404 = cls(
            error=error,
            request_id=request_id,
        )

        return get_api_tests_id_history_response_404
