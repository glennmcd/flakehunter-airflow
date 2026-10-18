from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_api_tests_id_history_response_200_data_item_status import (
    GetApiTestsIdHistoryResponse200DataItemStatus,
)

if TYPE_CHECKING:
    from ..models.get_api_tests_id_history_response_200_data_item_run import (
        GetApiTestsIdHistoryResponse200DataItemRun,
    )


T = TypeVar("T", bound="GetApiTestsIdHistoryResponse200DataItem")


@_attrs_define
class GetApiTestsIdHistoryResponse200DataItem:
    """
    Attributes:
        result_id (int):
        status (GetApiTestsIdHistoryResponse200DataItemStatus):
        head_sha (str):
        head_branch (None | str):
        occurrence_index (int):
        duration_seconds (float | None):
        failure_message (None | str):
        created_at (str):
        run (GetApiTestsIdHistoryResponse200DataItemRun):
    """

    result_id: int
    status: GetApiTestsIdHistoryResponse200DataItemStatus
    head_sha: str
    head_branch: None | str
    occurrence_index: int
    duration_seconds: float | None
    failure_message: None | str
    created_at: str
    run: GetApiTestsIdHistoryResponse200DataItemRun

    def to_dict(self) -> dict[str, Any]:
        result_id = self.result_id

        status = self.status.value

        head_sha = self.head_sha

        head_branch: None | str
        head_branch = self.head_branch

        occurrence_index = self.occurrence_index

        duration_seconds: float | None
        duration_seconds = self.duration_seconds

        failure_message: None | str
        failure_message = self.failure_message

        created_at = self.created_at

        run = self.run.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "resultId": result_id,
                "status": status,
                "headSha": head_sha,
                "headBranch": head_branch,
                "occurrenceIndex": occurrence_index,
                "durationSeconds": duration_seconds,
                "failureMessage": failure_message,
                "createdAt": created_at,
                "run": run,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_tests_id_history_response_200_data_item_run import (
            GetApiTestsIdHistoryResponse200DataItemRun,
        )

        d = dict(src_dict)
        result_id = d.pop("resultId")

        status = GetApiTestsIdHistoryResponse200DataItemStatus(d.pop("status"))

        head_sha = d.pop("headSha")

        def _parse_head_branch(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        head_branch = _parse_head_branch(d.pop("headBranch"))

        occurrence_index = d.pop("occurrenceIndex")

        def _parse_duration_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        duration_seconds = _parse_duration_seconds(d.pop("durationSeconds"))

        def _parse_failure_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        failure_message = _parse_failure_message(d.pop("failureMessage"))

        created_at = d.pop("createdAt")

        run = GetApiTestsIdHistoryResponse200DataItemRun.from_dict(d.pop("run"))

        get_api_tests_id_history_response_200_data_item = cls(
            result_id=result_id,
            status=status,
            head_sha=head_sha,
            head_branch=head_branch,
            occurrence_index=occurrence_index,
            duration_seconds=duration_seconds,
            failure_message=failure_message,
            created_at=created_at,
            run=run,
        )

        return get_api_tests_id_history_response_200_data_item
