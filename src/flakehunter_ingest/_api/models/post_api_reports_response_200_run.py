from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiReportsResponse200Run")


@_attrs_define
class PostApiReportsResponse200Run:
    """
    Attributes:
        id (int):
        github_run_id (int):
        attempt (int):
        head_sha (str):
    """

    id: int
    github_run_id: int
    attempt: int
    head_sha: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        github_run_id = self.github_run_id

        attempt = self.attempt

        head_sha = self.head_sha

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "githubRunId": github_run_id,
                "attempt": attempt,
                "headSha": head_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        github_run_id = d.pop("githubRunId")

        attempt = d.pop("attempt")

        head_sha = d.pop("headSha")

        post_api_reports_response_200_run = cls(
            id=id,
            github_run_id=github_run_id,
            attempt=attempt,
            head_sha=head_sha,
        )

        return post_api_reports_response_200_run
