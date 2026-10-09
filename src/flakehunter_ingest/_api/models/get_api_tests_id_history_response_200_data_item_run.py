from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="GetApiTestsIdHistoryResponse200DataItemRun")


@_attrs_define
class GetApiTestsIdHistoryResponse200DataItemRun:
    """
    Attributes:
        id (int):
        github_run_id (int):
        attempt (int):
        workflow_name (str):
        html_url (None | str):
    """

    id: int
    github_run_id: int
    attempt: int
    workflow_name: str
    html_url: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        github_run_id = self.github_run_id

        attempt = self.attempt

        workflow_name = self.workflow_name

        html_url: None | str
        html_url = self.html_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "githubRunId": github_run_id,
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

        github_run_id = d.pop("githubRunId")

        attempt = d.pop("attempt")

        workflow_name = d.pop("workflowName")

        def _parse_html_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        html_url = _parse_html_url(d.pop("htmlUrl"))

        get_api_tests_id_history_response_200_data_item_run = cls(
            id=id,
            github_run_id=github_run_id,
            attempt=attempt,
            workflow_name=workflow_name,
            html_url=html_url,
        )

        return get_api_tests_id_history_response_200_data_item_run
