from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v2_tests_id_failures_response_200_data_item import (
        GetApiV2TestsIdFailuresResponse200DataItem,
    )
    from ..models.get_api_v2_tests_id_failures_response_200_test import (
        GetApiV2TestsIdFailuresResponse200Test,
    )


T = TypeVar("T", bound="GetApiV2TestsIdFailuresResponse200")


@_attrs_define
class GetApiV2TestsIdFailuresResponse200:
    """
    Attributes:
        test (GetApiV2TestsIdFailuresResponse200Test):
        data (list[GetApiV2TestsIdFailuresResponse200DataItem]):
    """

    test: GetApiV2TestsIdFailuresResponse200Test
    data: list[GetApiV2TestsIdFailuresResponse200DataItem]

    def to_dict(self) -> dict[str, Any]:
        test = self.test.to_dict()

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "test": test,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_v2_tests_id_failures_response_200_data_item import (
            GetApiV2TestsIdFailuresResponse200DataItem,
        )
        from ..models.get_api_v2_tests_id_failures_response_200_test import (
            GetApiV2TestsIdFailuresResponse200Test,
        )

        d = dict(src_dict)
        test = GetApiV2TestsIdFailuresResponse200Test.from_dict(d.pop("test"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiV2TestsIdFailuresResponse200DataItem.from_dict(
                data_item_data
            )

            data.append(data_item)

        get_api_v2_tests_id_failures_response_200 = cls(
            test=test,
            data=data,
        )

        return get_api_v2_tests_id_failures_response_200
