from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV2ReportsResponse201Counts")


@_attrs_define
class PostApiV2ReportsResponse201Counts:
    """
    Attributes:
        suites (int):
        tests (int):
        passed (int):
        failed (int):
        error (int):
        skipped (int):
    """

    suites: int
    tests: int
    passed: int
    failed: int
    error: int
    skipped: int

    def to_dict(self) -> dict[str, Any]:
        suites = self.suites

        tests = self.tests

        passed = self.passed

        failed = self.failed

        error = self.error

        skipped = self.skipped

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "suites": suites,
                "tests": tests,
                "passed": passed,
                "failed": failed,
                "error": error,
                "skipped": skipped,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        suites = d.pop("suites")

        tests = d.pop("tests")

        passed = d.pop("passed")

        failed = d.pop("failed")

        error = d.pop("error")

        skipped = d.pop("skipped")

        post_api_v2_reports_response_201_counts = cls(
            suites=suites,
            tests=tests,
            passed=passed,
            failed=failed,
            error=error,
            skipped=skipped,
        )

        return post_api_v2_reports_response_201_counts
