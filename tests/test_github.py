
import json
import logging
from pathlib import Path

import httpx
import respx

from flakehunter_ingest.github import (
    download_first_unexpired_artifact,
    get_artifacts_spec_from_github,
    get_github_artifacts_url,
    get_github_repo_run_url,
    get_list_of_runs,
    get_runs_from_github,
    is_run_trusted,
    required_fields_exists,
)

logging.basicConfig(level=logging.DEBUG)
test_logger = logging.getLogger(__name__)

# discover_runs lists completed workflow runs for each configured repository,
# created in the data interval plus a 24-hour lookback 
# (GET /repos/{owner}/{repo}/actions/runs?status=completed&created=>=…). 
# It drops runs that the webhook would also refuse (see Trust) and returns one 
# small descriptor per run.

#test github API
#   test for successful responses from github API
#   test for empty responses from github API
#   test for extra records in the response from github API
#   test if github API only returns approved runs
#test handling of github API errors

#test happy path test with fixture
#test github API results
#   test for list of runs
#   test for required fields existence
#   test parsing of the results
#       test for parsing required fields
#       test for irregular values in required fields
#   test handling of missing fields

@respx.mock 
def test_github_download_zip():
    fixture_path = Path(__file__).parent / "fixtures" / "artifact_spec.json"
    zip_path = Path(__file__).parent / "fixtures" / "github_artifact.zip"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    url = fixture["artifacts"][0]["archive_download_url"]
    streamData = zip_path.read_bytes()
    respx.get(url).mock(return_value=httpx.Response(200, content=streamData))
    result = download_first_unexpired_artifact(fixture)
    assert result
    assert Path(result).exists()
    # Clean up the downloaded file
    if result and Path(result).exists():
        Path(result).unlink()   
        
@respx.mock 
def test_github_artifacts_fixture_httpx_call():
    repo_name = "flakehunter-test-fixture"
    repo_owner = "glennmcd"
    fixture_path = Path(__file__).parent / "fixtures" / "artifact_spec.json"
    strData = fixture_path.read_text(encoding="utf-8")
    url = get_github_artifacts_url(repo_owner, repo_name, artifact_id=11375895934)
    respx.get(url).mock(return_value=httpx.Response(200, json=strData))
    call_result = get_artifacts_spec_from_github(url)
    assert call_result is not None
    assert call_result == strData
    

@respx.mock 
def test_github_runs_httpx_call():
    repo_name = "flakehunter-test-fixture"
    repo_owner = "glennmcd"
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    url = get_github_repo_run_url(repo_owner,repo_name)
    respx.get(url).mock(return_value=httpx.Response(200, json=strData))
    call_result = get_runs_from_github(url)
    assert call_result is not None
    assert call_result == strData

def test_returns_list_of_runs():
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    list_of_runs = get_list_of_runs(strData)
    assert isinstance(list_of_runs, list)
    assert len(list_of_runs) == 10
    
    
def test_runs_have_required_fields():
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    list_of_runs = get_list_of_runs(strData)
    assert isinstance(list_of_runs, list)
    assert len(list_of_runs) == 10
    for run in list_of_runs:
        assert required_fields_exists(run) is True

def test_trust_logic():
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    list_of_runs = get_list_of_runs(strData)
    assert isinstance(list_of_runs, list)
    assert len(list_of_runs) == 10
    num_trusted_runs = 0
    for run in list_of_runs:
        assert required_fields_exists(run) is True
        if is_run_trusted(run,repo_id=1404833977):
            num_trusted_runs += 1
    assert num_trusted_runs > 0

def test_required_fields_exists():
    run = {
        "id": 1,
        "head_repository": {"full_name": "owner/repo"},
        "run_attempt": 1,
        "head_sha": "abc123",
        "head_branch": "main",
        "name": "test",
        "run_started_at": "2024-06-01T00:00:00Z",
        "artifacts_url": "https://example.com/artifacts",
        "event": "push"
        
    }
    assert required_fields_exists(run) is True

# def test_parsing_of_required_fields():
#     fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
#     data = json.loads(fixture_path.read_text(encoding="utf-8"))
#     parsed_result = "{}"
    
#     assert "id" in parsed_result
#     assert "head_repository" in parsed_result
#     assert "full_name" in parsed_result["head_repository"]



# def test_handling_of_missing_fields():
#     result = {}
#     assert "id" not in result
#     assert "head_repository" not in result
#     assert "full_name" not in result
#     assert "run_attempt" not in result
#     assert "head_sha" not in result
#     assert "head_branch" not in result
#     assert "name" not in result
#     assert "run_started_at" not in result
#     assert "webhook-artifact" not in result
#     assert "always" not in result

# def test_get_fixture():
#     url = f"https://api.github.com/repos/gmcdonald/flakehunter-test-fixture/actions/runs"
    
#     headers = {
#         "Accept": "application/vnd.github+json",
#         "Authorization": f"Bearer dev_token",
#         "X-GitHub-Api-Version": "2022-11-28",
#     }
    
#     with httpx.Client(headers=headers,timeout=10) as client:
#         response = client.get(url)
#         response.raise_for_status()
#         data = response.json()
#         fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
#         fixture_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        
    