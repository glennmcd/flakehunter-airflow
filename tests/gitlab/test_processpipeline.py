import gzip
import io
import xml.etree.ElementTree as ET
import zipfile

import httpx
import pytest
import respx

from flakehunter_ingest_gitlab.gitlab import get_http_client_gitlab
from flakehunter_ingest_gitlab.pipeline import GlPipeline
from flakehunter_ingest_gitlab.processpipeline import process_pipeline
from shared.limits import MAX_ARTIFACT_ZIP_BYTES

API = "https://gitlab.test/api/v4"
UPLOAD_BASE = "https://flakehunter.test"
SHA = "e" * 40

DISCOVERED = GlPipeline(id=100, project_id=5, sha=SHA, ref="main", status="success", source="push")
DETAILS = {
    "id": 100,
    "project_id": 5,
    "sha": SHA,
    "ref": "main",
    "status": "failed",
    "source": "push",
    "name": "Nightly",
    "started_at": "2026-10-01T12:00:00Z",
}


def make_zip(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def suite(name: str) -> str:
    return f'<testsuite name="{name}"><testcase classname="c" name="t"/></testsuite>'


def job(job_id: int, name: str, status: str = "success", size: int | None = 100) -> dict:
    artifacts = [{"file_type": "archive", "size": size}] if size is not None else []
    return {"id": job_id, "name": name, "status": status, "artifacts": artifacts}


@pytest.fixture
def client():
    with get_http_client_gitlab("https://gitlab.test", "read-token") as c:
        yield c


@pytest.fixture
def gitlab():
    with respx.mock(assert_all_called=False) as router:
        yield router


def mock_pipeline(gitlab, jobs: list[dict], details: dict = DETAILS):
    gitlab.get(f"{API}/projects/5/pipelines/100").mock(
        return_value=httpx.Response(200, json=details)
    )
    gitlab.get(f"{API}/projects/5/pipelines/100/jobs").mock(
        return_value=httpx.Response(200, json=jobs)
    )
    return gitlab.post(f"{UPLOAD_BASE}/api/v2/reports").mock(return_value=httpx.Response(201))


def mock_archive(gitlab, job_id: int, content: bytes):
    return gitlab.get(f"{API}/projects/5/jobs/{job_id}/artifacts").mock(
        return_value=httpx.Response(200, content=content)
    )


def test_headers_come_from_the_pipeline(client, gitlab):
    upload = mock_pipeline(gitlab, [job(1, "test", "failed"), job(2, "test")])
    mock_archive(gitlab, 2, make_zip({"junit.xml": suite("a")}))

    result = process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE)

    assert result is not None and result.outcome == "stored"
    sent = upload.calls.last.request.headers
    assert sent["x-fh-ci-source"] == "gitlab_ci"
    assert sent["x-fh-run-id"] == "100"
    assert sent["x-fh-run-attempt"] == "2"
    assert sent["x-fh-sha"] == SHA
    assert sent["x-fh-branch"] == "main"
    assert sent["x-fh-workflow"] == "Nightly"
    assert sent["x-fh-timestamp"] == "2026-10-01T12:00:00+00:00"
    assert sent["x-fh-report-key"] == "webhook-artifact"
    assert sent["authorization"] == "Bearer upload-token"


def test_null_started_at_and_name_are_omitted(client, gitlab):
    details = {**DETAILS, "status": "canceled", "name": None, "started_at": None}
    upload = mock_pipeline(gitlab, [job(1, "test")], details)
    mock_archive(gitlab, 1, make_zip({"junit.xml": suite("a")}))

    process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE)

    sent = upload.calls.last.request.headers
    assert "x-fh-timestamp" not in sent
    assert "x-fh-workflow" not in sent


def test_xml_from_every_current_job_is_merged(client, gitlab):
    jobs = [job(1, "unit", "failed"), job(2, "lint", size=None), job(3, "e2e"), job(4, "unit")]
    upload = mock_pipeline(gitlab, jobs)
    retried = mock_archive(gitlab, 1, make_zip({"junit.xml": suite("stale")}))
    mock_archive(gitlab, 3, make_zip({"junit.xml": suite("e2e")}))
    mock_archive(gitlab, 4, make_zip({"junit.xml": suite("unit")}))

    process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE)

    assert not retried.called
    merged = ET.fromstring(gzip.decompress(upload.calls.last.request.content))
    assert [s.get("name") for s in merged.findall("testsuite")] == ["e2e", "unit"]


def test_oversized_archives_are_left_out(client, gitlab):
    jobs = [job(1, "listed", size=MAX_ARTIFACT_ZIP_BYTES + 1), job(2, "streamed"), job(3, "ok")]
    upload = mock_pipeline(gitlab, jobs)
    listed = mock_archive(gitlab, 1, b"")
    mock_archive(gitlab, 2, b"x" * (MAX_ARTIFACT_ZIP_BYTES + 1))
    mock_archive(gitlab, 3, make_zip({"junit.xml": suite("ok")}))

    process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE)

    assert not listed.called
    merged = ET.fromstring(gzip.decompress(upload.calls.last.request.content))
    assert [s.get("name") for s in merged.findall("testsuite")] == ["ok"]


def test_nothing_is_uploaded_without_archives(client, gitlab):
    upload = mock_pipeline(gitlab, [job(1, "build", size=None)])
    assert process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE) is None
    assert not upload.called


def test_nothing_is_uploaded_when_the_archives_hold_no_xml(client, gitlab):
    """As in the test project: JUnit only in reports:junit, node_modules in the archive."""
    reports_only = {**job(1, "run-tests", "failed"), "artifacts": [{"file_type": "junit"}]}
    upload = mock_pipeline(gitlab, [reports_only, job(2, "install-dependencies")])
    mock_archive(gitlab, 2, make_zip({"node_modules/a/package.json": "{}"}))

    assert process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE) is None
    assert not upload.called


@pytest.mark.parametrize(
    ("details", "jobs"),
    [
        ({**DETAILS, "status": "running"}, [job(1, "test")]),
        (DETAILS, [job(1, "test", "failed"), job(2, "test", "pending")]),
    ],
    ids=["pipeline running", "job retry pending"],
)
def test_a_pipeline_running_again_is_left_for_later(client, gitlab, details, jobs):
    upload = mock_pipeline(gitlab, jobs, details)
    assert process_pipeline(client, DISCOVERED, "upload-token", UPLOAD_BASE) is None
    assert not upload.called
