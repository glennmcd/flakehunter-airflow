from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v2_repos_id_summary_response_200_repo import (
        GetApiV2ReposIdSummaryResponse200Repo,
    )
    from ..models.get_api_v2_repos_id_summary_response_200_totals import (
        GetApiV2ReposIdSummaryResponse200Totals,
    )
    from ..models.get_api_v2_repos_id_summary_response_200_window import (
        GetApiV2ReposIdSummaryResponse200Window,
    )


T = TypeVar("T", bound="GetApiV2ReposIdSummaryResponse200")


@_attrs_define
class GetApiV2ReposIdSummaryResponse200:
    """
    Attributes:
        repo (GetApiV2ReposIdSummaryResponse200Repo):
        window (GetApiV2ReposIdSummaryResponse200Window):
        totals (GetApiV2ReposIdSummaryResponse200Totals):
        last_run_at (None | str):
    """

    repo: GetApiV2ReposIdSummaryResponse200Repo
    window: GetApiV2ReposIdSummaryResponse200Window
    totals: GetApiV2ReposIdSummaryResponse200Totals
    last_run_at: None | str

    def to_dict(self) -> dict[str, Any]:
        repo = self.repo.to_dict()

        window = self.window.to_dict()

        totals = self.totals.to_dict()

        last_run_at: None | str
        last_run_at = self.last_run_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "repo": repo,
                "window": window,
                "totals": totals,
                "lastRunAt": last_run_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_api_v2_repos_id_summary_response_200_repo import (
            GetApiV2ReposIdSummaryResponse200Repo,
        )
        from ..models.get_api_v2_repos_id_summary_response_200_totals import (
            GetApiV2ReposIdSummaryResponse200Totals,
        )
        from ..models.get_api_v2_repos_id_summary_response_200_window import (
            GetApiV2ReposIdSummaryResponse200Window,
        )

        d = dict(src_dict)
        repo = GetApiV2ReposIdSummaryResponse200Repo.from_dict(d.pop("repo"))

        window = GetApiV2ReposIdSummaryResponse200Window.from_dict(d.pop("window"))

        totals = GetApiV2ReposIdSummaryResponse200Totals.from_dict(d.pop("totals"))

        def _parse_last_run_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_run_at = _parse_last_run_at(d.pop("lastRunAt"))

        get_api_v2_repos_id_summary_response_200 = cls(
            repo=repo,
            window=window,
            totals=totals,
            last_run_at=last_run_at,
        )

        return get_api_v2_repos_id_summary_response_200
