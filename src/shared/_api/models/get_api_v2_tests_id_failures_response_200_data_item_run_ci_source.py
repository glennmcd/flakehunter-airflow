from enum import StrEnum


class GetApiV2TestsIdFailuresResponse200DataItemRunCiSource(StrEnum):
    GITHUB_ACTIONS = "github_actions"

    def __str__(self) -> str:
        return str(self.value)
