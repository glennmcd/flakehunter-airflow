from enum import StrEnum


class PostApiV2ReportsXFhCiSource(StrEnum):
    GITHUB_ACTIONS = "github_actions"

    def __str__(self) -> str:
        return str(self.value)
