from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GlPipeline:
    id: int
    project_id: int
    sha: str
    ref: str
    status: str
    source: str
    name: str | None = None  # single-pipeline endpoint only
    started_at: datetime | None = None  # single-pipeline endpoint only; null if no job started

    @classmethod
    def from_api(cls, raw: dict) -> "GlPipeline":
        """Build from a GitLab pipeline object (list item or single pipeline).

        Raises KeyError/ValueError if malformed.
        """
        started_at = raw.get("started_at")
        return cls(
            id=int(raw["id"]),
            project_id=int(raw["project_id"]),
            sha=raw["sha"],
            ref=raw["ref"],
            status=raw["status"],
            source=raw["source"],
            name=raw.get("name") or None,
            started_at=datetime.fromisoformat(started_at) if started_at else None,
        )
