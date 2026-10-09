from enum import StrEnum


class GetApiTestsIdHistoryResponse200DataItemStatus(StrEnum):
    ERROR = "error"
    FAILED = "failed"
    PASSED = "passed"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
