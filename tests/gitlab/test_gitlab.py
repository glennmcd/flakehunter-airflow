from datetime import UTC, datetime

import httpx
import pytest
import respx

from flakehunter_ingest_gitlab.gitlab import (
    archive_size,
    current_jobs,
    get_http_client_gitlab,
    list_pipelines,
    qualify_pipelines,
    run_attempt,
    validate_projects,
)
from flakehunter_ingest_gitlab.pipeline import GlPipeline
from flakehunter_ingest_gitlab.trust import is_pipeline_trusted, merge_request_iid

API = "https://gitlab.test/api/v4"
SHA = "c" * 40


def pipeline(**overrides) -> GlPipeline:
    values = dict(
        id=100, project_id=5, sha=SHA, ref="main", status="success", source="push", name=None
    )
    return GlPipeline(**{**values, **overrides})


def job(job_id: int, name: str, status: str = "success") -> dict:
    return {"id": job_id, "name": name, "status": status}


@pytest.fixture
def client():
    with get_http_client_gitlab("https://gitlab.test/", "read-token") as c:
        yield c


def test_from_api_reads_the_single_pipeline_payload():
    parsed = GlPipeline.from_api(
        {
            "id": 100,
            "project_id": 5,
            "sha": SHA,
            "ref": "main",
            "status": "failed",
            "source": "push",
            "name": "Nightly",
            "started_at": "2026-10-01T12:00:00.123Z",
        }
    )
    assert parsed == pipeline(status="failed", name="Nightly", started_at=parsed.started_at)
    assert parsed.started_at == datetime(2026, 10, 1, 12, 0, 0, 123000, tzinfo=UTC)


def test_from_api_accepts_a_null_started_at_and_empty_name():
    raw = {"id": 1, "project_id": 5, "sha": SHA, "ref": "main", "status": "canceled"}
    parsed = GlPipeline.from_api({**raw, "source": "web", "name": "", "started_at": None})
    assert parsed.started_at is None and parsed.name is None


@pytest.mark.parametrize(
    ("jobs", "attempt"),
    [
        ([job(1, "test"), job(2, "lint")], 1),
        ([job(1, "test", "failed"), job(2, "lint"), job(3, "test")], 2),
        ([job(1, "a"), job(2, "b"), job(3, "a"), job(4, "b"), job(5, "a")], 4),
    ],
    ids=["no retries", "one retry", "retries across jobs"],
)
def test_run_attempt_counts_retried_jobs(jobs, attempt):
    assert run_attempt(jobs) == attempt


def test_current_jobs_keeps_the_latest_of_each_name():
    jobs = [job(3, "test"), job(1, "test", "failed"), job(2, "lint")]
    assert [j["id"] for j in current_jobs(jobs)] == [2, 3]


def test_archive_size():
    assert archive_size({"artifacts": [{"file_type": "junit", "size": 9}]}) is None
    assert archive_size({"artifacts": [{"file_type": "archive", "size": 42}]}) == 42
    assert archive_size({"artifacts_file": {"filename": "a.zip", "size": 7}}) == 7
    assert archive_size({}) is None


def test_validate_projects():
    assert validate_projects("[5, 6]") == [5, 6]
    assert validate_projects('[5, "group/project", true, -1, 7]') == [5, 7]
    assert validate_projects('{"id": 5}') == []
    assert validate_projects("not json") == []


@pytest.mark.parametrize("source", ["push", "schedule", "web"])
def test_trusted_sources(source):
    assert is_pipeline_trusted(pipeline(source=source))


@pytest.mark.parametrize(
    "source", ["api", "trigger", "pipeline", "parent_pipeline", "external", "chat"]
)
def test_other_sources_are_not_trusted(source):
    assert not is_pipeline_trusted(pipeline(source=source))


def test_merge_request_trust_needs_a_same_project_merge_request():
    mr = pipeline(source="merge_request_event", ref="refs/merge-requests/12/head")
    assert merge_request_iid(mr) == 12
    assert is_pipeline_trusted(mr, {"source_project_id": 5, "target_project_id": 5})
    assert not is_pipeline_trusted(mr, {"source_project_id": 9, "target_project_id": 5})
    assert not is_pipeline_trusted(mr, None)


def test_merged_results_ref_has_no_iid():
    assert merge_request_iid(pipeline(ref="refs/merge-requests/12/merge")) is None


@respx.mock
def test_list_pipelines_follows_pages(client):
    route = respx.get(f"{API}/projects/5/pipelines")
    route.side_effect = [
        httpx.Response(200, json=[{**_raw(1)}], headers={"x-next-page": "2"}),
        httpx.Response(200, json=[{**_raw(2)}], headers={"x-next-page": ""}),
    ]
    found = list_pipelines(client, 5, datetime(2026, 10, 1, tzinfo=UTC))
    assert [p.id for p in found] == [1, 2]
    first = route.calls[0].request.url.params
    assert first["updated_after"] == "2026-10-01T00:00:00+00:00"
    assert first["per_page"] == "100"
    assert route.calls[0].request.headers["authorization"] == "Bearer read-token"


@respx.mock
def test_qualify_pipelines(client):
    respx.get(f"{API}/projects/5/merge_requests/12").mock(
        return_value=httpx.Response(200, json={"source_project_id": 5, "target_project_id": 5})
    )
    respx.get(f"{API}/projects/5/merge_requests/13").mock(
        return_value=httpx.Response(200, json={"source_project_id": 9, "target_project_id": 5})
    )
    pipelines = [
        pipeline(id=1),
        pipeline(id=2, status="running"),
        pipeline(id=3, sha="d" * 64),
        pipeline(id=4, sha=SHA.upper()),
        pipeline(id=5, source="api"),
        pipeline(id=6, source="merge_request_event", ref="refs/merge-requests/12/head"),
        pipeline(id=7, source="merge_request_event", ref="refs/merge-requests/13/head"),
        pipeline(id=8, source="merge_request_event", ref="refs/merge-requests/12/merge"),
        pipeline(id=9, status="canceled"),
    ]
    valid, skipped = qualify_pipelines(client, pipelines)
    assert [p.id for p in valid] == [1, 6, 9]
    assert [p.id for p in skipped] == [3, 4, 5, 7, 8]  # running pipelines are neither


def _raw(pipeline_id: int) -> dict:
    return {
        "id": pipeline_id,
        "project_id": 5,
        "sha": SHA,
        "ref": "main",
        "status": "success",
        "source": "push",
    }
