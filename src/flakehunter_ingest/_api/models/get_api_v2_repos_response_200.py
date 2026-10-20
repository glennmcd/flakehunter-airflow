from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v2_repos_response_200_data_item import (
        GetApiV2ReposResponse200DataItem,
    )
    from ..models.get_api_v2_repos_response_200_page import GetApiV2ReposResponse200Page


T = TypeVar("T", bound="GetApiV2ReposResponse200")


@_attrs_define
class GetApiV2ReposResponse200:
    """
    Attributes:
        data (list[GetApiV2ReposResponse200DataItem]):
        page (GetApiV2ReposResponse200Page):
    """

    data: list[GetApiV2ReposResponse200DataItem]
    page: GetApiV2ReposResponse200Page

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
        from ..models.get_api_v2_repos_response_200_data_item import (
            GetApiV2ReposResponse200DataItem,
        )
        from ..models.get_api_v2_repos_response_200_page import (
            GetApiV2ReposResponse200Page,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiV2ReposResponse200DataItem.from_dict(data_item_data)

            data.append(data_item)

        page = GetApiV2ReposResponse200Page.from_dict(d.pop("page"))

        get_api_v2_repos_response_200 = cls(
            data=data,
            page=page,
        )

        return get_api_v2_repos_response_200
