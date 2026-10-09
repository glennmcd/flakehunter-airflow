from enum import StrEnum


class GetApiTestsIdFailuresResponse200DataItemStatus(StrEnum):
    ERROR = "error"
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
