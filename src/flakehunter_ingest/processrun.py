# NO: upsert to workflowRuns db, gets run.id back
# NO: checks if report already uploaded for run, exits if so
# lists github's run artifacts,  gets first expired
# downloads artifact, size limited
# extracts xml into suites
# POST /api/reports data in headers?
# NO: inserts summary into reports
# NO: inserts suites
# NO: updates fetched at with now() in db
# NO: wrapped in tx


import json
import logging

from flakehunter_ingest.client import (
    RunHeaders,
    UploadError,
    UploadResult,
    make_client,
    upload_report,
)
from flakehunter_ingest.ghartifactspec import GhArtifactSpec
from flakehunter_ingest.ghworkflowrun import GhWorkflowRun
from flakehunter_ingest.github import (
    download_artifact,
    get_http_client_github,
    get_resp_from_githubapi,
)
from flakehunter_ingest.junit import merge_junit
from flakehunter_ingest.limits import MAX_ARTIFACT_ZIP_BYTES, ArtifactRejected
from flakehunter_ingest.safezip import read_xml_entries

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
    xml_data: dict[str, bytes]
    try:
        with get_http_client_github(github_pat) as client:
            zip_bytes = download_artifact(client, artifactSpec.archive_download_url)
            if not zip_bytes:
                logger.error(f"Failed to download artifact for run: {run.artifacts_url}")
                return
            logger.info(f"Downloaded artifact, size: {len(zip_bytes)} bytes")

        xml_data = read_xml_entries(zip_bytes)
        suites_file_xml = merge_junit(xml_data)
    except ArtifactRejected as e:
        logger.error(f"Artifact rejected for run {run.id}: {e}")
        return

    # At this point, suites_file contains
    # the combined XML of all test suites extracted from the artifact.
    # upload to flakehunter API or any other relevant endpoint
    api_client = make_client(uploadUrl, uploadToken)

    headers = RunHeaders(
        run.id,
        run.run_attempt,
        run.head_sha,
        run.head_branch or "main",
        run.name,
        run.run_started_at.isoformat(),
    )
    try:
        upload_result: UploadResult = upload_report(api_client, suites_file_xml, headers)
        if upload_result.status_code in [200, 201]:
            logger.info(f"Successfully uploaded report for run: {run.artifacts_url}")
        else:
            logger.error(f"Failed to upload report for run: {run.artifacts_url}")
            logger.error(f"upload_result: {upload_result}")
    except UploadError as e:
        logger.error(f"Upload error for run: {run.artifacts_url} - {e}")


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
