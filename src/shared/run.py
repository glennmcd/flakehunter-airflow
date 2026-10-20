from dataclasses import dataclass
from datetime import datetime

from shared.client import RunHeaders


@dataclass(frozen=True, slots=True)
class CiRun:
    """One CI run, independent of the CI system. Every value comes from that system's API."""

    run_id: int
    run_attempt: int
    sha: str
    branch: str
    workflow: str
    started_at: datetime

    def headers(self) -> RunHeaders:
        return RunHeaders(
            self.run_id,
            self.run_attempt,
            self.sha,
            self.branch,
            self.workflow,
            self.started_at.isoformat(),
        )
