"""Record GitLab API fixtures from a real project into tests/fixtures.

Usage: GITLAB_TOKEN=... uv run python scripts/get_gitlab_fixture.py <project> [<pipeline_id>]
<project> is the numeric id or the path (group/project). GITLAB_URL defaults to https://gitlab.com.
Without a pipeline id, the latest pipeline is used. Prints the numeric project id, which is what
the flakehunter_gitlab_projects Variable needs.
Writes gitlab_pipelines.json, gitlab_pipeline.json, gitlab_jobs.json and, for the first job with
an artifacts archive, gitlab_job_artifact.zip. Check the JSON for anything private before
committing it.
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import httpx

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


def write_json(name: str, data: object) -> None:
    (FIXTURES / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    base_url = os.getenv("GITLAB_URL", "https://gitlab.com").rstrip("/")
    headers = {"Authorization": f"Bearer {os.getenv('GITLAB_TOKEN')}"}

    with httpx.Client(
        base_url=f"{base_url}/api/v4", headers=headers, timeout=30, follow_redirects=True
    ) as client:
        project = client.get(f"/projects/{quote(sys.argv[1], safe='')}")
        project.raise_for_status()
        project_id = project.json()["id"]
        print(f"project id: {project_id}")

        pipelines = client.get(f"/projects/{project_id}/pipelines", params={"per_page": 20})
        pipelines.raise_for_status()
        write_json("gitlab_pipelines.json", pipelines.json())

        pipeline_id = int(sys.argv[2]) if len(sys.argv) == 3 else pipelines.json()[0]["id"]
        pipeline = client.get(f"/projects/{project_id}/pipelines/{pipeline_id}")
        pipeline.raise_for_status()
        write_json("gitlab_pipeline.json", pipeline.json())

        jobs = client.get(
            f"/projects/{project_id}/pipelines/{pipeline_id}/jobs",
            params={"include_retried": "true", "per_page": 100},
        )
        jobs.raise_for_status()
        write_json("gitlab_jobs.json", jobs.json())

        for job in jobs.json():
            if any(a.get("file_type") == "archive" for a in job.get("artifacts") or []):
                archive = client.get(f"/projects/{project_id}/jobs/{job['id']}/artifacts")
                archive.raise_for_status()
                (FIXTURES / "gitlab_job_artifact.zip").write_bytes(archive.content)
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
