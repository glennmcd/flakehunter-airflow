import json
import logging
import os
import random
import string
import tempfile
from pathlib import Path

import httpx

from flakehunter_ingest.ghworkflowrun import GhWorkflowRun
from flakehunter_ingest.trust import is_run_trusted

logger = logging.getLogger(__name__)


class GitHubRunData:
    def __init__(self, run: dict):
        self.run = run


def download_artifact(client: httpx.Client, zip_url: str) -> Path | None:
    # Placeholder implementation
    # Placeholder for actual download logic
    logger.info(f"Downloading artifact from {zip_url}")
    # get random filename for download
    root_temp_dir = tempfile.mkdtemp(prefix="fh_scratch")
    artifact_path = Path(root_temp_dir) / "artifact.zip"

    try:
        response = client.get(zip_url)
        response.raise_for_status()
        with open(artifact_path, "wb") as f:
            f.write(response.content)
    except httpx.HTTPError as e:
        logger.error(f"Failed to download artifact zip: {zip_url} {e}")
        return None

    return artifact_path or None


def download_first_unexpired_artifact(fixture: dict) -> str:
    # Placeholder implementation
    if "artifacts" in fixture and fixture["artifacts"]:
        first = next((x for x in fixture["artifacts"] if not x.get("expired", False)), None)
        if first is None:
            logger.error("No unexpired artifacts found.")
            return ""
        zip_url = first.get("archive_download_url")
        if not zip_url:
            logger.error("No download URL found for the first unexpired artifact.")
            return ""
        # Placeholder for actual download logic
        logger.info(f"Downloading artifact from {zip_url}")
        # get random filename for download
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        random_filename = f"archive_{suffix}.zip"
        temp_dir = tempfile.gettempdir()
        fixture_path = os.path.join(temp_dir, random_filename)
        YOUR_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {YOUR_GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            with httpx.Client(headers=headers, timeout=20, follow_redirects=True) as client:
                response = client.get(zip_url)
                response.raise_for_status()
                with open(fixture_path, "wb") as f:
                    f.write(response.content)
        except httpx.HTTPError as e:
            logger.error(f"Failed to download artifact zip: {zip_url} {e}")
            return ""

        return fixture_path
    return ""


def get_github_repo_run_url(repo_owner: str, repo_name: str) -> str:
    return f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs"


def get_http_client_github(token: str) -> httpx.Client:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    return httpx.Client(headers=headers, timeout=10)


def construct_http_client(url: str, token: str) -> httpx.Client:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    return httpx.Client(headers=headers, timeout=10, base_url=url)


def get_resp_from_githubapi(client: httpx.Client, url: str) -> str:

    try:
        response = client.get(url=url)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch from GitHub: {e}")
        return ""


def qualify_discovered_runs(
    runs: list[GhWorkflowRun],
) -> tuple[list[GhWorkflowRun], list[GhWorkflowRun]]:
    valid_runs = []
    skipped_runs = []
    for run in runs:
        if is_run_trusted(run):
            valid_runs.append(run)
        else:
            skipped_runs.append(run)
    return valid_runs, skipped_runs


def get_list_of_runs(gitHubResult: str) -> list[GhWorkflowRun]:
    # Placeholder implementation
    data = None
    try:
        data = json.loads(gitHubResult)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {gitHubResult}")
        logger.error(f"{e}")
        return []
    # iterate over the children of the "workflow_runs" key into a list
    list_of_runs = []
    if "workflow_runs" in data:
        for a_run in data["workflow_runs"]:
            try:
                run_data = GhWorkflowRun.from_api(a_run)
            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse run data: {a_run}")
                logger.error(f"{e}")
                continue

            if not is_run_trusted(run_data):
                logger.error(f"Run is not trusted: {a_run}")
                continue

            list_of_runs.append(run_data)

    return list_of_runs


def extract_required_fields(a_run: dict) -> dict:
    return {
        "id": a_run.get("id"),
        "head_repository": a_run.get("head_repository"),
        "repository": a_run.get("repository"),
        "run_attempt": a_run.get("run_attempt"),
        "head_sha": a_run.get("head_sha"),
        "head_branch": a_run.get("head_branch"),
        "name": a_run.get("name"),
        "run_started_at": a_run.get("run_started_at"),
        "artifacts_url": a_run.get("artifacts_url"),
        "event": a_run.get("event"),
    }


def required_fields_exists(run: dict) -> bool:
    required_fields = [
        "id",
        "head_repository",
        "repository",
        "run_attempt",
        "head_sha",
        "head_branch",
        "name",
        "run_started_at",
        "artifacts_url",
        "event",
    ]
    return all(field in run for field in required_fields)
