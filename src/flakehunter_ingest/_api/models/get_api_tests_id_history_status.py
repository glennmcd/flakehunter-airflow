from enum import StrEnum


class GetApiTestsIdHistoryStatus(StrEnum):
    ERROR = "error"
    FAILED = "failed"
    PASSED = "passed"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
