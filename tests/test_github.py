import io
import json
import logging
import zipfile
from pathlib import Path

import httpx
import pytest
import respx

from flakehunter_ingest import github
from flakehunter_ingest.github import (
    download_artifact,
    get_github_repo_run_url,
    get_http_client_github,
    get_list_of_runs,
    get_resp_from_githubapi,
)
from shared.limits import ArtifactRejected

logging.basicConfig(level=logging.DEBUG)
test_logger = logging.getLogger(__name__)

# discover_runs lists completed workflow runs for each configured repository,
# created in the data interval plus a 24-hour lookback
# (GET /repos/{owner}/{repo}/actions/runs?status=completed&created=>=…).
# It drops runs that the webhook would also refuse (see Trust) and returns one
# small descriptor per run.

# test github API
#   test for successful responses from github API
#   test for empty responses from github API
#   test for extra records in the response from github API
#   test if github API only returns approved runs
# test handling of github API errors

# test happy path test with fixture
# test github API results
#   test for list of runs
#   test for required fields existence
#   test parsing of the results
#       test for parsing required fields
#       test for irregular values in required fields
#   test handling of missing fields


@respx.mock
def test_content_length_too_large(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(github, "MAX_ARTIFACT_ZIP_BYTES", 1)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("test.xml", "<testsuite></testsuite>")
    buffer.seek(0)

    headers = {"Content-Length": str(buffer.getbuffer().nbytes)}
    respx.get("https://example.com/artifacts").mock(
        return_value=httpx.Response(200, content=buffer.getvalue(), headers=headers)
    )
    with (
        pytest.raises(
            ArtifactRejected,
            match="Artifact exceeds maximum allowed size in content-length header",
        ),
        get_http_client_github("dev_token") as client,
    ):
        download_artifact(client, "https://example.com/artifacts")


@respx.mock
def test_content_body_too_large(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(github, "MAX_ARTIFACT_ZIP_BYTES", 1)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("test.xml", "<testsuite></testsuite>")
    buffer.seek(0)
    respx.get("https://example.com/artifacts").mock(
        return_value=httpx.Response(200, stream=httpx.ByteStream(buffer.getvalue())),
    )
    with (
        pytest.raises(
            ArtifactRejected,
            match="Artifact exceeds maximum allowed size in file stream",
        ),
        get_http_client_github("dev_token") as client,
    ):
        download_artifact(client, "https://example.com/artifacts")


@respx.mock
def test_content_length_invalid_is_ignored():
    body = b"zip bytes"
    respx.get("https://example.com/artifacts").mock(
        return_value=httpx.Response(200, content=body, headers={"Content-Length": "abc"})
    )
    with get_http_client_github("dev_token") as client:
        assert download_artifact(client, "https://example.com/artifacts") == body


@respx.mock
def test_content_returns_404():

    respx.get("https://example.com/artifacts").mock(return_value=httpx.Response(404))
    with get_http_client_github("dev_token") as client:
        assert download_artifact(client, "https://example.com/artifacts") is None


@respx.mock
def test_github_runs_httpx_call():
    repo_name = "flakehunter-test-fixture"
    repo_owner = "glennmcd"
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    url = get_github_repo_run_url(repo_owner, repo_name)

    respx.get(url).mock(return_value=httpx.Response(200, json=strData))

    with get_http_client_github("dev_token") as client:
        call_result = get_resp_from_githubapi(client, url)
        assert call_result is not None
        assert json.loads(call_result) == strData


def test_returns_list_of_runs():
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    list_of_runs = get_list_of_runs(strData)
    assert isinstance(list_of_runs, list)
    assert len(list_of_runs) == 10
