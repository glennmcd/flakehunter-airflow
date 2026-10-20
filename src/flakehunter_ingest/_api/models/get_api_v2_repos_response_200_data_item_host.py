from enum import StrEnum


class GetApiV2ReposResponse200DataItemHost(StrEnum):
    GITHUB = "github"

    def __str__(self) -> str:
        return str(self.value)
