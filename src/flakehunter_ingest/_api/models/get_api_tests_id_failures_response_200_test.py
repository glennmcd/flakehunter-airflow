from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="GetApiTestsIdFailuresResponse200Test")


@_attrs_define
class GetApiTestsIdFailuresResponse200Test:
    """
    Attributes:
        id (int):
        repo_id (int):
        classname (str):
        name (str):
    """

    id: int
    repo_id: int
    classname: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        repo_id = self.repo_id

        classname = self.classname

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "repoId": repo_id,
                "classname": classname,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        repo_id = d.pop("repoId")

        classname = d.pop("classname")

        name = d.pop("name")

        get_api_tests_id_failures_response_200_test = cls(
            id=id,
            repo_id=repo_id,
            classname=classname,
            name=name,
        )

        return get_api_tests_id_failures_response_200_test
