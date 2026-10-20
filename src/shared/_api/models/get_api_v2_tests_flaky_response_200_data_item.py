from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV2TestsFlakyResponse200DataItem")


@_attrs_define
class GetApiV2TestsFlakyResponse200DataItem:
    """
    Attributes:
        test_id (int):
        classname (str):
        name (str):
        shas_run (int):
        flaky_shas (int):
        flake_rate (float):
        last_flaky_at (str):
    """

    test_id: int
    classname: str
    name: str
    shas_run: int
    flaky_shas: int
    flake_rate: float
    last_flaky_at: str

    def to_dict(self) -> dict[str, Any]:
        test_id = self.test_id

        classname = self.classname

        name = self.name

        shas_run = self.shas_run

        flaky_shas = self.flaky_shas

        flake_rate = self.flake_rate

        last_flaky_at = self.last_flaky_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "testId": test_id,
                "classname": classname,
                "name": name,
                "shasRun": shas_run,
                "flakyShas": flaky_shas,
                "flakeRate": flake_rate,
                "lastFlakyAt": last_flaky_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        test_id = d.pop("testId")

        classname = d.pop("classname")

        name = d.pop("name")

        shas_run = d.pop("shasRun")

        flaky_shas = d.pop("flakyShas")

        flake_rate = d.pop("flakeRate")

        last_flaky_at = d.pop("lastFlakyAt")

        get_api_v2_tests_flaky_response_200_data_item = cls(
            test_id=test_id,
            classname=classname,
            name=name,
            shas_run=shas_run,
            flaky_shas=flaky_shas,
            flake_rate=flake_rate,
            last_flaky_at=last_flaky_at,
        )

        return get_api_v2_tests_flaky_response_200_data_item
