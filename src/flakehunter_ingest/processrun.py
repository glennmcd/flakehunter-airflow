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
import os
from asyncio.log import logger
from pathlib import Path

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
from flakehunter_ingest.junit import get_combined_artifact
from flakehunter_ingest.safezip import safe_zip_check_extract


def process_ghworkflowrun(run: GhWorkflowRun, uploadToken: str, uploadUrl: str):

    artifactSpec = get_first_non_expired_artifact(run, uploadToken)
    if artifactSpec is None:
        logger.error(f"No non-expired artifact found for run: {run.artifacts_url}")
        return

    zip_path: Path | None = None
    with get_http_client_github(uploadToken) as client:
        zip_path = download_artifact(client, artifactSpec.archive_download_url)
        if not zip_path:
            logger.error(f"Failed to download artifact for run: {run.artifacts_url}")
            return

    output_dir = extract_artifact(zip_path, Path("extracted"))

    suites_file = construct_suites(output_dir)
    suites_file_xml: bytes = suites_file.read_bytes()

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
    except UploadError as e:
        logger.error(f"Upload error for run: {run.artifacts_url} - {e}")


def construct_suites(output_dir: Path) -> Path:
    xmlPaths: list[Path] = []
    root_dir = Path(output_dir)
    for path in root_dir.rglob("*.xml"):
        if path.is_file():
            print(f"File: {path}")
            xmlPaths.append(path)

    suites_path = output_dir.parent / "suites.xml"
    get_combined_artifact(xmlPaths, suites_path)
    return suites_path


def extract_artifact(zip_path: Path, extract_to: Path) -> Path:
    output_dir = Path(os.path.splitext(os.path.basename(zip_path))[0]) / extract_to
    safe_zip_check_extract(zip_path, extract_to)
    return output_dir


def get_first_non_expired_artifact(run: GhWorkflowRun, uploadToken: str) -> GhArtifactSpec | None:
    artifacts: dict | None = None
    with get_http_client_github(uploadToken) as client:
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
