from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GhWorkflowRun:
    id: int
    run_attempt: int
    head_sha: str
    head_branch: str | None
    name: str
    run_started_at: datetime
    event: str
    head_repository_id: int | None
    repository_id: int | None
    repository_owner: str | None
    repository_name: str | None
    artifacts_url: str

    @classmethod
    def from_api(cls, raw: dict) -> "GhWorkflowRun":
        """Build from one item of GitHub's `workflow_runs`. \
            Raises KeyError/ValueError if malformed."""
        head_repo = raw.get("head_repository") or {}
        repo = raw.get("repository") or {}
        return cls(
            id=int(raw["id"]),
            run_attempt=int(raw["run_attempt"]),
            head_sha=raw["head_sha"],
            head_branch=raw.get("head_branch"),
            name=raw["name"],
            run_started_at=datetime.fromisoformat(raw["run_started_at"]),
            event=raw["event"],
            head_repository_id=head_repo.get("id"),
            repository_id=repo.get("id"),
            repository_name=repo.get("name"),
            repository_owner=repo.get("full_name", {}).split("/")[0]
            if "full_name" in repo
            else None,
            artifacts_url=raw["artifacts_url"],
        )
