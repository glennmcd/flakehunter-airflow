from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.get_api_tests_id_failures_response_200_data_item_status import (
    GetApiTestsIdFailuresResponse200DataItemStatus,
)

if TYPE_CHECKING:
    from ..models.get_api_tests_id_failures_response_200_data_item_run import (
        GetApiTestsIdFailuresResponse200DataItemRun,
    )


T = TypeVar("T", bound="GetApiTestsIdFailuresResponse200DataItem")


@_attrs_define
class GetApiTestsIdFailuresResponse200DataItem:
    """
    Attributes:
        result_id (int):
        status (GetApiTestsIdFailuresResponse200DataItemStatus):
        head_sha (str):
        head_branch (None | str):
        failure_message (None | str):
        created_at (str):
        run (GetApiTestsIdFailuresResponse200DataItemRun):
    """

    result_id: int
    status: GetApiTestsIdFailuresResponse200DataItemStatus
    head_sha: str
    head_branch: None | str
    failure_message: None | str
    created_at: str
    run: GetApiTestsIdFailuresResponse200DataItemRun

    def to_dict(self) -> dict[str, Any]:
        result_id = self.result_id

        status = self.status.value

        head_sha = self.head_sha

        head_branch: None | str
        head_branch = self.head_branch

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
                "failureMessage": failure_message,
                "createdAt": created_at,
                "run": run,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_tests_id_failures_response_200_data_item_run import (
            GetApiTestsIdFailuresResponse200DataItemRun,
        )

        d = dict(src_dict)
        result_id = d.pop("resultId")

        status = GetApiTestsIdFailuresResponse200DataItemStatus(d.pop("status"))

        head_sha = d.pop("headSha")

        def _parse_head_branch(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        head_branch = _parse_head_branch(d.pop("headBranch"))

        def _parse_failure_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        failure_message = _parse_failure_message(d.pop("failureMessage"))

        created_at = d.pop("createdAt")

        run = GetApiTestsIdFailuresResponse200DataItemRun.from_dict(d.pop("run"))

        get_api_tests_id_failures_response_200_data_item = cls(
            result_id=result_id,
            status=status,
            head_sha=head_sha,
            head_branch=head_branch,
            failure_message=failure_message,
            created_at=created_at,
            run=run,
        )

        return get_api_tests_id_failures_response_200_data_item
