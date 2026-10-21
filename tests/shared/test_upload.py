import gzip
import io
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import replace
from datetime import UTC, datetime

import httpx
import respx

from shared.run import CiRun
from shared.upload import upload_run_artifacts

UPLOAD_BASE = "https://flakehunter.test"
UPLOAD_URL = f"{UPLOAD_BASE}/api/v2/reports"

RUN = CiRun(
    run_id=7,
    run_attempt=2,
    sha="b" * 40,
    branch="main",
    workflow="CI",
    started_at=datetime(2026, 10, 1, 12, 0, tzinfo=UTC),
)


def make_zip(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def suite(name: str) -> str:
    return f'<testsuite name="{name}"><testcase classname="c" name="t"/></testsuite>'


def test_headers_come_from_the_run():
    headers = RUN.headers()
    assert (headers.run_id, headers.run_attempt, headers.sha) == (7, 2, "b" * 40)
    assert (headers.branch, headers.workflow) == ("main", "CI")
    assert headers.timestamp == "2026-10-01T12:00:00+00:00"
    assert headers.ci_source is None


def test_ci_source_and_missing_start_time():
    headers = replace(RUN, started_at=None, ci_source="gitlab_ci").headers()
    assert (headers.timestamp, headers.ci_source) == ("", "gitlab_ci")


@respx.mock
def test_ci_source_is_sent_when_set():
    route = respx.post(UPLOAD_URL).mock(return_value=httpx.Response(201))
    run = replace(RUN, ci_source="gitlab_ci")

    upload_run_artifacts(run, [make_zip({"a.xml": suite("a")})], UPLOAD_BASE, "token")

    assert route.calls.last.request.headers["x-fh-ci-source"] == "gitlab_ci"


@respx.mock
def test_one_archive_is_uploaded_with_the_run_headers():
    route = respx.post(UPLOAD_URL).mock(return_value=httpx.Response(201))

    result = upload_run_artifacts(RUN, [make_zip({"a.xml": suite("a")})], UPLOAD_BASE, "token")

    assert result is not None and result.outcome == "stored"
    sent = route.calls.last.request.headers
    assert sent["x-fh-run-id"] == "7"
    assert sent["x-fh-run-attempt"] == "2"
    assert sent["x-fh-sha"] == "b" * 40
    assert sent["x-fh-branch"] == "main"
    assert sent["x-fh-workflow"] == "CI"
    assert sent["x-fh-timestamp"] == "2026-10-01T12:00:00+00:00"


@respx.mock
def test_same_named_files_from_several_archives_are_all_merged():
    route = respx.post(UPLOAD_URL).mock(return_value=httpx.Response(201))
    zips = [make_zip({"junit.xml": suite("first")}), make_zip({"junit.xml": suite("second")})]

    upload_run_artifacts(RUN, zips, UPLOAD_BASE, "token")

    merged = ET.fromstring(gzip.decompress(route.calls.last.request.content))
    assert [s.get("name") for s in merged.findall("testsuite")] == ["first", "second"]


@respx.mock
def test_archives_without_xml_are_not_uploaded():
    route = respx.post(UPLOAD_URL).mock(return_value=httpx.Response(201))
    zips = [make_zip({"node_modules/a/package.json": "{}"}), make_zip({})]

    result = upload_run_artifacts(RUN, zips, UPLOAD_BASE, "token")

    assert result is None
    assert not route.called


@respx.mock
def test_rejected_archive_is_not_uploaded():
    route = respx.post(UPLOAD_URL).mock(return_value=httpx.Response(201))

    result = upload_run_artifacts(RUN, [b"not a zip"], UPLOAD_BASE, "token")

    assert result is None
    assert not route.called
