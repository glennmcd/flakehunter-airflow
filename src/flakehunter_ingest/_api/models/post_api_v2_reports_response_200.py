from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v2_reports_response_200_counts import (
        PostApiV2ReportsResponse200Counts,
    )
    from ..models.post_api_v2_reports_response_200_run import (
        PostApiV2ReportsResponse200Run,
    )


T = TypeVar("T", bound="PostApiV2ReportsResponse200")


@_attrs_define
class PostApiV2ReportsResponse200:
    """Duplicate upload; counts are those of the original.

    Attributes:
        run (PostApiV2ReportsResponse200Run):
        duplicate (bool):
        counts (PostApiV2ReportsResponse200Counts):
    """

    run: PostApiV2ReportsResponse200Run
    duplicate: bool
    counts: PostApiV2ReportsResponse200Counts

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
        from ..models.post_api_v2_reports_response_200_counts import (
            PostApiV2ReportsResponse200Counts,
        )
        from ..models.post_api_v2_reports_response_200_run import (
            PostApiV2ReportsResponse200Run,
        )

        d = dict(src_dict)
        run = PostApiV2ReportsResponse200Run.from_dict(d.pop("run"))

        duplicate = d.pop("duplicate")

        counts = PostApiV2ReportsResponse200Counts.from_dict(d.pop("counts"))

        post_api_v2_reports_response_200 = cls(
            run=run,
            duplicate=duplicate,
            counts=counts,
        )

        return post_api_v2_reports_response_200
