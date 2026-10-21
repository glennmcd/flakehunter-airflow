import logging

import httpx

from flakehunter_ingest_gitlab.gitlab import (
    FINISHED_JOB_STATUSES,
    TERMINAL_STATUSES,
    archive_size,
    current_jobs,
    get_pipeline,
    list_jobs,
    run_attempt,
)
from flakehunter_ingest_gitlab.pipeline import GlPipeline
from shared.client import UploadResult
from shared.download import download_artifact
from shared.limits import MAX_ARTIFACT_ZIP_BYTES, ArtifactRejected
from shared.run import CiRun
from shared.upload import upload_run_artifacts

logger = logging.getLogger(__name__)

CI_SOURCE = "gitlab_ci"


def process_pipeline(
    client: httpx.Client, pipeline: GlPipeline, upload_token: str, upload_url: str
) -> UploadResult | None:
    """Download the archive of every current job, merge their XML and upload it as one run.

    Returns None when nothing is uploaded; the reason is logged.
    """
    details = get_pipeline(client, pipeline.project_id, pipeline.id)  # name and started_at
    jobs = list_jobs(client, pipeline.project_id, pipeline.id)
    current = current_jobs(jobs)
    if details.status not in TERMINAL_STATUSES or any(
        job["status"] not in FINISHED_JOB_STATUSES for job in current
    ):
        logger.info(f"Pipeline {pipeline.id} is running again; left for a later run")
        return None

    zips: list[bytes] = []
    for job in current:
        size = archive_size(job)
        if size is None:
            continue
        if size > MAX_ARTIFACT_ZIP_BYTES:
            logger.error(f"Archive of job {job['id']} too large for pipeline {pipeline.id}")
            continue
        try:
            zip_bytes = download_artifact(
                client, f"/projects/{pipeline.project_id}/jobs/{job['id']}/artifacts"
            )
        except ArtifactRejected as e:
            logger.error(f"Archive of job {job['id']} rejected for pipeline {pipeline.id}: {e}")
            continue
        if not zip_bytes:
            logger.error(f"Failed to download archive of job {job['id']}")
            continue
        zips.append(zip_bytes)

    if not zips:
        logger.error(f"No job archives to upload for pipeline {pipeline.id}")
        return None
    return upload_run_artifacts(
        to_ci_run(details, run_attempt(jobs)), zips, upload_url, upload_token
    )


def to_ci_run(pipeline: GlPipeline, attempt: int) -> CiRun:
    return CiRun(
        run_id=pipeline.id,
        run_attempt=attempt,
        sha=pipeline.sha,
        branch=pipeline.ref,
        workflow=pipeline.name or "",
        started_at=pipeline.started_at,
        ci_source=CI_SOURCE,
    )
