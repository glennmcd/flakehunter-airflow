from enum import StrEnum


class PostApiV2ReportsXFhCiSource(StrEnum):
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"

    def __str__(self) -> str:
        return str(self.value)
