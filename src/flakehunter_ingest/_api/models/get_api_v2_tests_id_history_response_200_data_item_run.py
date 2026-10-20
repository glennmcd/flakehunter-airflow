from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_api_v2_tests_id_history_response_200_data_item_run_ci_source import (
    GetApiV2TestsIdHistoryResponse200DataItemRunCiSource,
)

T = TypeVar("T", bound="GetApiV2TestsIdHistoryResponse200DataItemRun")


@_attrs_define
class GetApiV2TestsIdHistoryResponse200DataItemRun:
    """
    Attributes:
        id (int):
        ci_run_id (int):
        ci_source (GetApiV2TestsIdHistoryResponse200DataItemRunCiSource):
        attempt (int):
        workflow_name (str):
        html_url (None | str):
    """

    id: int
    ci_run_id: int
    ci_source: GetApiV2TestsIdHistoryResponse200DataItemRunCiSource
    attempt: int
    workflow_name: str
    html_url: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        ci_run_id = self.ci_run_id

        ci_source = self.ci_source.value

        attempt = self.attempt

        workflow_name = self.workflow_name

        html_url: None | str
        html_url = self.html_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "ciRunId": ci_run_id,
                "ciSource": ci_source,
                "attempt": attempt,
                "workflowName": workflow_name,
                "htmlUrl": html_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        ci_run_id = d.pop("ciRunId")

        ci_source = GetApiV2TestsIdHistoryResponse200DataItemRunCiSource(
            d.pop("ciSource")
        )

        attempt = d.pop("attempt")

        workflow_name = d.pop("workflowName")

        def _parse_html_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        html_url = _parse_html_url(d.pop("htmlUrl"))

        get_api_v2_tests_id_history_response_200_data_item_run = cls(
            id=id,
            ci_run_id=ci_run_id,
            ci_source=ci_source,
            attempt=attempt,
            workflow_name=workflow_name,
            html_url=html_url,
        )

        return get_api_v2_tests_id_history_response_200_data_item_run
