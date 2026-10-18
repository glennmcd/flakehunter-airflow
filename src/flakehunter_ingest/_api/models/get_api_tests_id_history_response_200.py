from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_tests_id_history_response_200_data_item import (
        GetApiTestsIdHistoryResponse200DataItem,
    )
    from ..models.get_api_tests_id_history_response_200_page import (
        GetApiTestsIdHistoryResponse200Page,
    )
    from ..models.get_api_tests_id_history_response_200_test import (
        GetApiTestsIdHistoryResponse200Test,
    )


T = TypeVar("T", bound="GetApiTestsIdHistoryResponse200")


@_attrs_define
class GetApiTestsIdHistoryResponse200:
    """
    Attributes:
        test (GetApiTestsIdHistoryResponse200Test):
        data (list[GetApiTestsIdHistoryResponse200DataItem]):
        page (GetApiTestsIdHistoryResponse200Page):
    """

    test: GetApiTestsIdHistoryResponse200Test
    data: list[GetApiTestsIdHistoryResponse200DataItem]
    page: GetApiTestsIdHistoryResponse200Page

    def to_dict(self) -> dict[str, Any]:
        test = self.test.to_dict()

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        page = self.page.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "test": test,
                "data": data,
                "page": page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_tests_id_history_response_200_data_item import (
            GetApiTestsIdHistoryResponse200DataItem,
        )
        from ..models.get_api_tests_id_history_response_200_page import (
            GetApiTestsIdHistoryResponse200Page,
        )
        from ..models.get_api_tests_id_history_response_200_test import (
            GetApiTestsIdHistoryResponse200Test,
        )

        d = dict(src_dict)
        test = GetApiTestsIdHistoryResponse200Test.from_dict(d.pop("test"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiTestsIdHistoryResponse200DataItem.from_dict(
                data_item_data
            )

            data.append(data_item)

        page = GetApiTestsIdHistoryResponse200Page.from_dict(d.pop("page"))

        get_api_tests_id_history_response_200 = cls(
            test=test,
            data=data,
            page=page,
        )

        return get_api_tests_id_history_response_200
