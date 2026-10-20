from enum import StrEnum


class GetApiV2TestsIdHistoryResponse200DataItemStatus(StrEnum):
    ERROR = "error"
    FAILED = "failed"
    PASSED = "passed"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
