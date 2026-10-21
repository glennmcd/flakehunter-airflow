import json
import logging
import re
from datetime import datetime

import httpx

from flakehunter_ingest_gitlab.pipeline import GlPipeline
from flakehunter_ingest_gitlab.trust import is_pipeline_trusted, merge_request_iid

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = frozenset({"success", "failed", "canceled"})
# Job states that can remain in a finished pipeline; anything else means a retry is under way.
FINISHED_JOB_STATUSES = frozenset({"success", "failed", "canceled", "skipped", "manual"})
SHA1 = re.compile(r"[0-9a-f]{40}")
PER_PAGE = 100
MAX_PAGES = 50


def get_http_client_gitlab(base_url: str, token: str) -> httpx.Client:
    """Client for the GitLab REST API at base_url (e.g. https://gitlab.com).

    The token goes in Authorization rather than PRIVATE-TOKEN: httpx drops Authorization when a
    redirect leaves the host, as artifact downloads may do to object storage.
    """
    return httpx.Client(
        base_url=f"{base_url.rstrip('/')}/api/v4",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
        follow_redirects=True,
    )


def get_all_pages(client: httpx.Client, path: str, params: dict | None = None) -> list[dict]:
    """GET every page of a list endpoint. HTTP errors propagate, so the task retries."""
    items: list[dict] = []
    page = "1"
    for _ in range(MAX_PAGES):
        response = client.get(path, params={**(params or {}), "per_page": PER_PAGE, "page": page})
        response.raise_for_status()
        batch = response.json()
        items.extend(batch)
        page = response.headers.get("x-next-page", "")
        if not page or not batch:
            return items
    logger.warning(f"Stopped after {MAX_PAGES} pages of {path}")
    return items


def validate_projects(projects_str: str) -> list[int]:
    try:
        projects = json.loads(projects_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode projects JSON: {e}")
        return []
    if not isinstance(projects, list):
        logger.error(f"Projects should be a list: {projects}")
        return []
    valid = []
    for project in projects:
        if isinstance(project, bool) or not isinstance(project, int) or project <= 0:
            logger.error(f"Invalid project id: {project}")
            continue
        valid.append(project)
    return valid


def list_pipelines(
    client: httpx.Client, project_id: int, updated_after: datetime
) -> list[GlPipeline]:
    raw = get_all_pages(
        client, f"/projects/{project_id}/pipelines", {"updated_after": updated_after.isoformat()}
    )
    pipelines = []
    for item in raw:
        try:
            pipelines.append(GlPipeline.from_api(item))
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse pipeline {item.get('id')}: {e}")
    return pipelines


def get_pipeline(client: httpx.Client, project_id: int, pipeline_id: int) -> GlPipeline:
    response = client.get(f"/projects/{project_id}/pipelines/{pipeline_id}")
    response.raise_for_status()
    return GlPipeline.from_api(response.json())


def get_merge_request(client: httpx.Client, project_id: int, iid: int) -> dict | None:
    response = client.get(f"/projects/{project_id}/merge_requests/{iid}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def qualify_pipelines(
    client: httpx.Client, pipelines: list[GlPipeline]
) -> tuple[list[GlPipeline], list[GlPipeline]]:
    """Split finished pipelines into (to upload, skipped). Unfinished ones wait for a later run."""
    valid = []
    skipped = []
    for pipeline in pipelines:
        if pipeline.status not in TERMINAL_STATUSES:
            continue
        if not SHA1.fullmatch(pipeline.sha):
            logger.warning(f"Skipping pipeline {pipeline.id}: sha is not 40 lowercase hex")
            skipped.append(pipeline)
            continue
        merge_request = None
        if pipeline.source == "merge_request_event":
            iid = merge_request_iid(pipeline)
            if iid is not None:
                merge_request = get_merge_request(client, pipeline.project_id, iid)
        if not is_pipeline_trusted(pipeline, merge_request):
            logger.warning(f"Skipping pipeline {pipeline.id}: not trusted ({pipeline.source})")
            skipped.append(pipeline)
            continue
        valid.append(pipeline)
    return valid, skipped


def list_jobs(client: httpx.Client, project_id: int, pipeline_id: int) -> list[dict]:
    """Every job of the pipeline, retried ones included."""
    return get_all_pages(
        client,
        f"/projects/{project_id}/pipelines/{pipeline_id}/jobs",
        {"include_retried": "true"},
    )


def current_jobs(jobs: list[dict]) -> list[dict]:
    """The latest job per name. Job names are unique in a pipeline; a retry adds a job of the same
    name with a higher id."""
    latest: dict[str, dict] = {}
    for job in jobs:
        name = job["name"]
        if name not in latest or job["id"] > latest[name]["id"]:
            latest[name] = job
    return sorted(latest.values(), key=lambda job: job["id"])


def run_attempt(jobs: list[dict]) -> int:
    """1 + the number of retried jobs: stable for a finished pipeline, +1 with every job retry."""
    return 1 + len(jobs) - len(current_jobs(jobs))


def archive_size(job: dict) -> int | None:
    """Size of the job's artifacts archive, or None if it has none."""
    for artifact in job.get("artifacts") or []:
        if artifact.get("file_type") == "archive":
            return int(artifact.get("size") or 0)
    artifacts_file = job.get("artifacts_file")
    return int(artifacts_file.get("size") or 0) if artifacts_file else None
