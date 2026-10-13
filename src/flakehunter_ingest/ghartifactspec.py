from attr import dataclass


@dataclass(frozen=True, slots=True)
class GhArtifactSpec:
    id: int
    archive_download_url: str
    expired: bool
    size_in_bytes: int

    @classmethod
    def from_api(cls, raw: dict) -> "GhArtifactSpec":
        return cls(
            id=raw["id"],
            archive_download_url=raw["archive_download_url"],
            expired=raw["expired"],
            size_in_bytes=raw["size_in_bytes"],
        )
