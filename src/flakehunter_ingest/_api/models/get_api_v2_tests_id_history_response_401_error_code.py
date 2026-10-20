from enum import StrEnum


class GetApiV2TestsIdHistoryResponse401ErrorCode(StrEnum):
    FORBIDDEN = "forbidden"
    INTERNAL_ERROR = "internal_error"
    INVALID_REPORT = "invalid_report"
    NOT_FOUND = "not_found"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    VALIDATION_ERROR = "validation_error"

    def __str__(self) -> str:
        return str(self.value)
