from enum import StrEnum


class PostApiV2ReportsContentEncoding(StrEnum):
    GZIP = "gzip"

    def __str__(self) -> str:
        return str(self.value)
