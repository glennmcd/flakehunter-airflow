from datetime import UTC, datetime

import httpx
import respx

from flakehunter_ingest.ghworkflowrun import GhWorkflowRun
from shared.limits import MAX_ARTIFACT_ZIP_BYTES
from flakehunter_ingest.processrun import process_ghworkflowrun

ARTIFACTS_URL = "https://api.github.com/repos/owner/repo/actions/runs/1/artifacts"
DOWNLOAD_URL = "https://api.github.com/repos/owner/repo/actions/artifacts/2/zip"
UPLOAD_BASE = "https://flakehunter.test"

RUN = GhWorkflowRun(
    id=1,
    run_attempt=1,
    head_sha="a" * 40,
    head_branch="main",
    name="Test",
    run_started_at=datetime(2026, 10, 1, tzinfo=UTC),
    event="push",
    head_repository_id=10,
    repository_id=10,
    repository_owner="owner",
    repository_name="repo",
    artifacts_url=ARTIFACTS_URL,
)


def test_listed_size_over_limit_skips_download():
    listing = {
        "artifacts": [
            {
                "id": 2,
                "archive_download_url": DOWNLOAD_URL,
                "expired": False,
                "size_in_bytes": MAX_ARTIFACT_ZIP_BYTES + 1,
            }
        ]
    }
    with respx.mock(assert_all_called=False) as router:
        listed = router.get(ARTIFACTS_URL).mock(return_value=httpx.Response(200, json=listing))
        download = router.get(DOWNLOAD_URL).mock(return_value=httpx.Response(200, content=b""))
        upload = router.post(f"{UPLOAD_BASE}/api/v2/reports").mock(return_value=httpx.Response(201))

        process_ghworkflowrun(RUN, "upload-token", UPLOAD_BASE, "dev_token")

    assert listed.called  # the size check ran, rather than an earlier failure
    assert not download.called
    assert not upload.called
