# NO: upsert to workflowRuns db, gets run.id back
# NO: checks if report already uploaded for run, exits if so
# lists github's run artifacts,  gets first expired
# downloads artifact, size limited
# extracts xml into suites
# POST /api/v2/reports data in headers?
# NO: inserts summary into reports
# NO: inserts suites
# NO: updates fetched at with now() in db
# NO: wrapped in tx


import json
import logging

from flakehunter_ingest_github.ghartifactspec import GhArtifactSpec
from flakehunter_ingest_github.ghworkflowrun import GhWorkflowRun
from flakehunter_ingest_github.github import get_http_client_github, get_resp_from_githubapi
from shared.download import download_artifact
from shared.limits import MAX_ARTIFACT_ZIP_BYTES, ArtifactRejected
from shared.run import CiRun
from shared.upload import upload_run_artifacts

logger = logging.getLogger(__name__)


def process_ghworkflowrun(run: GhWorkflowRun, uploadToken: str, uploadUrl: str, github_pat: str):

    artifactSpec = get_first_non_expired_artifact(run, github_pat)
    if artifactSpec is None:
        logger.error(f"No non-expired artifact found for run: {run.artifacts_url}")
        return
    logger.info(f"Found non-expired artifact for run: {run.artifacts_url}")
    if artifactSpec.size_in_bytes > MAX_ARTIFACT_ZIP_BYTES:
        logger.error(f"Artifact too large for run {run.id}")
        return
    zip_bytes: bytes | None = None
    try:
        with get_http_client_github(github_pat) as client:
            zip_bytes = download_artifact(client, artifactSpec.archive_download_url)
            if not zip_bytes:
                logger.error(f"Failed to download artifact for run: {run.artifacts_url}")
                return
            logger.info(f"Downloaded artifact, size: {len(zip_bytes)} bytes")
    except ArtifactRejected as e:
        logger.error(f"Artifact rejected for run {run.id}: {e}")
        return

    upload_run_artifacts(to_ci_run(run), [zip_bytes], uploadUrl, uploadToken)


def to_ci_run(run: GhWorkflowRun) -> CiRun:
    return CiRun(
        run_id=run.id,
        run_attempt=run.run_attempt,
        sha=run.head_sha,
        branch=run.head_branch or "main",
        workflow=run.name,
        started_at=run.run_started_at,
    )


def get_first_non_expired_artifact(run: GhWorkflowRun, github_pat: str) -> GhArtifactSpec | None:
    artifacts: dict | None = None
    with get_http_client_github(github_pat) as client:
        response = get_resp_from_githubapi(client, run.artifacts_url)
        if response:
            try:
                artifacts = json.loads(response)
            except json.JSONDecodeError:
                artifacts = None
    if artifacts is None:
        logger.error(f"Failed to fetch artifacts for run: {run.artifacts_url}")
        return

    artifactSpec: GhArtifactSpec | None = None

    for artifact in artifacts.get("artifacts", []):
        a_spec = GhArtifactSpec.from_api(artifact)
        if not a_spec.expired:
            artifactSpec = a_spec
            break

    return artifactSpec
