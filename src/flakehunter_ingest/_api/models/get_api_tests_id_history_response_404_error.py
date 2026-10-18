from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

from ..models.get_api_tests_id_history_response_404_error_code import (
    GetApiTestsIdHistoryResponse404ErrorCode,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_tests_id_history_response_404_error_details_item import (
        GetApiTestsIdHistoryResponse404ErrorDetailsItem,
    )


T = TypeVar("T", bound="GetApiTestsIdHistoryResponse404Error")


@_attrs_define
class GetApiTestsIdHistoryResponse404Error:
    """
    Attributes:
        code (GetApiTestsIdHistoryResponse404ErrorCode):
        message (str):
        details (list[GetApiTestsIdHistoryResponse404ErrorDetailsItem] | Unset):
    """

    code: GetApiTestsIdHistoryResponse404ErrorCode
    message: str
    details: list[GetApiTestsIdHistoryResponse404ErrorDetailsItem] | Unset = UNSET

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
        from ..models.get_api_tests_id_history_response_404_error_details_item import (
            GetApiTestsIdHistoryResponse404ErrorDetailsItem,
        )

        d = dict(src_dict)
        code = GetApiTestsIdHistoryResponse404ErrorCode(d.pop("code"))

        message = d.pop("message")

        _details = d.pop("details", UNSET)
        details: list[GetApiTestsIdHistoryResponse404ErrorDetailsItem] | Unset = UNSET
        if _details is not UNSET:
            details = []
            for details_item_data in _details:
                details_item = (
                    GetApiTestsIdHistoryResponse404ErrorDetailsItem.from_dict(
                        details_item_data
                    )
                )

                details.append(details_item)

        get_api_tests_id_history_response_404_error = cls(
            code=code,
            message=message,
            details=details,
        )

        return get_api_tests_id_history_response_404_error
