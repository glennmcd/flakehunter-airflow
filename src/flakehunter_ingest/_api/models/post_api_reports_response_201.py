from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_reports_response_201_counts import (
        PostApiReportsResponse201Counts,
    )
    from ..models.post_api_reports_response_201_run import PostApiReportsResponse201Run


T = TypeVar("T", bound="PostApiReportsResponse201")


@_attrs_define
class PostApiReportsResponse201:
    """Report stored.

    Attributes:
        run (PostApiReportsResponse201Run):
        duplicate (bool):
        counts (PostApiReportsResponse201Counts):
    """

    run: PostApiReportsResponse201Run
    duplicate: bool
    counts: PostApiReportsResponse201Counts

    def to_dict(self) -> dict[str, Any]:
        run = self.run.to_dict()

        duplicate = self.duplicate

        counts = self.counts.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "run": run,
                "duplicate": duplicate,
                "counts": counts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.post_api_reports_response_201_counts import (
            PostApiReportsResponse201Counts,
        )
        from ..models.post_api_reports_response_201_run import (
            PostApiReportsResponse201Run,
        )

        d = dict(src_dict)
        run = PostApiReportsResponse201Run.from_dict(d.pop("run"))

        duplicate = d.pop("duplicate")

        counts = PostApiReportsResponse201Counts.from_dict(d.pop("counts"))

        post_api_reports_response_201 = cls(
            run=run,
            duplicate=duplicate,
            counts=counts,
        )

        return post_api_reports_response_201
