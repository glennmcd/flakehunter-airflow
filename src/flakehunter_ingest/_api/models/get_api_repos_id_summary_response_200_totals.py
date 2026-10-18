from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiReposIdSummaryResponse200Totals")


@_attrs_define
class GetApiReposIdSummaryResponse200Totals:
    """
    Attributes:
        runs (int):
        tests (int):
        results (int):
        pass_rate (float | None):
        flaky_tests (int):
        flaky_shas (int):
    """

    runs: int
    tests: int
    results: int
    pass_rate: float | None
    flaky_tests: int
    flaky_shas: int

    def to_dict(self) -> dict[str, Any]:
        runs = self.runs

        tests = self.tests

        results = self.results

        pass_rate: float | None
        pass_rate = self.pass_rate

        flaky_tests = self.flaky_tests

        flaky_shas = self.flaky_shas

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "runs": runs,
                "tests": tests,
                "results": results,
                "passRate": pass_rate,
                "flakyTests": flaky_tests,
                "flakyShas": flaky_shas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        runs = d.pop("runs")

        tests = d.pop("tests")

        results = d.pop("results")

        def _parse_pass_rate(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        pass_rate = _parse_pass_rate(d.pop("passRate"))

        flaky_tests = d.pop("flakyTests")

        flaky_shas = d.pop("flakyShas")

        get_api_repos_id_summary_response_200_totals = cls(
            runs=runs,
            tests=tests,
            results=results,
            pass_rate=pass_rate,
            flaky_tests=flaky_tests,
            flaky_shas=flaky_shas,
        )

        return get_api_repos_id_summary_response_200_totals
