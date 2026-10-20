from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v2_tests_flaky_response_200_data_item import (
        GetApiV2TestsFlakyResponse200DataItem,
    )
    from ..models.get_api_v2_tests_flaky_response_200_page import (
        GetApiV2TestsFlakyResponse200Page,
    )


T = TypeVar("T", bound="GetApiV2TestsFlakyResponse200")


@_attrs_define
class GetApiV2TestsFlakyResponse200:
    """
    Attributes:
        data (list[GetApiV2TestsFlakyResponse200DataItem]):
        page (GetApiV2TestsFlakyResponse200Page):
    """

    data: list[GetApiV2TestsFlakyResponse200DataItem]
    page: GetApiV2TestsFlakyResponse200Page

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        page = self.page.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
                "page": page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_v2_tests_flaky_response_200_data_item import (
            GetApiV2TestsFlakyResponse200DataItem,
        )
        from ..models.get_api_v2_tests_flaky_response_200_page import (
            GetApiV2TestsFlakyResponse200Page,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiV2TestsFlakyResponse200DataItem.from_dict(data_item_data)

            data.append(data_item)

        page = GetApiV2TestsFlakyResponse200Page.from_dict(d.pop("page"))

        get_api_v2_tests_flaky_response_200 = cls(
            data=data,
            page=page,
        )

        return get_api_v2_tests_flaky_response_200
