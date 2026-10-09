from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.get_api_tests_id_failures_response_200_data_item import (
        GetApiTestsIdFailuresResponse200DataItem,
    )
    from ..models.get_api_tests_id_failures_response_200_test import (
        GetApiTestsIdFailuresResponse200Test,
    )


T = TypeVar("T", bound="GetApiTestsIdFailuresResponse200")


@_attrs_define
class GetApiTestsIdFailuresResponse200:
    """
    Attributes:
        test (GetApiTestsIdFailuresResponse200Test):
        data (list[GetApiTestsIdFailuresResponse200DataItem]):
    """

    test: GetApiTestsIdFailuresResponse200Test
    data: list[GetApiTestsIdFailuresResponse200DataItem]

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
        from ..models.get_api_tests_id_failures_response_200_data_item import (
            GetApiTestsIdFailuresResponse200DataItem,
        )
        from ..models.get_api_tests_id_failures_response_200_test import (
            GetApiTestsIdFailuresResponse200Test,
        )

        d = dict(src_dict)
        test = GetApiTestsIdFailuresResponse200Test.from_dict(d.pop("test"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiTestsIdFailuresResponse200DataItem.from_dict(
                data_item_data
            )

            data.append(data_item)

        get_api_tests_id_failures_response_200 = cls(
            test=test,
            data=data,
        )

        return get_api_tests_id_failures_response_200
