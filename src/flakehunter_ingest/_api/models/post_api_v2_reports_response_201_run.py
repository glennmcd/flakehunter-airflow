from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v2_reports_response_201_run_ci_source import (
    PostApiV2ReportsResponse201RunCiSource,
)

T = TypeVar("T", bound="PostApiV2ReportsResponse201Run")


@_attrs_define
class PostApiV2ReportsResponse201Run:
    """
    Attributes:
        id (int):
        ci_run_id (int):
        ci_source (PostApiV2ReportsResponse201RunCiSource):
        attempt (int):
        head_sha (str):
    """

    id: int
    ci_run_id: int
    ci_source: PostApiV2ReportsResponse201RunCiSource
    attempt: int
    head_sha: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        ci_run_id = self.ci_run_id

        ci_source = self.ci_source.value

        attempt = self.attempt

        head_sha = self.head_sha

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "ciRunId": ci_run_id,
                "ciSource": ci_source,
                "attempt": attempt,
                "headSha": head_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        ci_run_id = d.pop("ciRunId")

        ci_source = PostApiV2ReportsResponse201RunCiSource(d.pop("ciSource"))

        attempt = d.pop("attempt")

        head_sha = d.pop("headSha")

        post_api_v2_reports_response_201_run = cls(
            id=id,
            ci_run_id=ci_run_id,
            ci_source=ci_source,
            attempt=attempt,
            head_sha=head_sha,
        )

        return post_api_v2_reports_response_201_run
