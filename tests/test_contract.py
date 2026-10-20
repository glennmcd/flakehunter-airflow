"""The client must follow contract/openapi.json (the pinned FlakeHunter API v2 spec)."""

import json
import re
from dataclasses import fields
from pathlib import Path

import httpx
import respx

from flakehunter_ingest.client import REPORT_KEY, RunHeaders, upload_report
from tests.conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "contract" / "openapi.json").read_text(encoding="utf-8"))
OP = SPEC["paths"]["/api/v2/reports"]["post"]
PARAMS = {p["name"]: p for p in OP["parameters"] if p["in"] == "header"}


def test_pinned_version():
    assert SPEC["info"]["version"] == "2.0.0"


@respx.mock
def test_sent_headers_are_declared_and_valid(client, headers):
    route = respx.post(f"{BASE}/api/v2/reports").mock(
        return_value=httpx.Response(201, json={"run": {}, "duplicate": False, "counts": {}})
    )
    upload_report(client, b"<testsuite/>", headers)
    sent = {
        k: v
        for k, v in route.calls.last.request.headers.items()
        if k.startswith("x-fh-") or k == "content-encoding"
    }

    required = {n for n, p in PARAMS.items() if p["required"]}
    assert required <= sent.keys(), "client omits a required header"
    assert sent.keys() <= PARAMS.keys(), "client sends a header the spec does not declare"

    for name, value in sent.items():
        schema = PARAMS[name]["schema"]
        if "pattern" in schema:
            assert re.fullmatch(schema["pattern"], value), name
        if "enum" in schema:
            assert value in schema["enum"], name
        if schema.get("type") == "integer":
            assert 0 < int(value) <= schema["maximum"], name
        if schema.get("maxLength"):
            assert len(value) <= schema["maxLength"], name


def test_report_key_within_spec():
    schema = PARAMS["x-fh-report-key"]["schema"]
    assert schema["minLength"] <= len(REPORT_KEY) <= schema["maxLength"]


def test_run_headers_cover_the_documented_set():
    assert {f.name for f in fields(RunHeaders)} == {
        "run_id",
        "run_attempt",
        "sha",
        "branch",
        "workflow",
        "timestamp",
    }


def test_documented_statuses_are_handled():
    assert set(OP["responses"]) == {"200", "201", "400", "401", "413", "422", "429"}


@respx.mock
def test_ci_source_is_left_to_the_github_default(client, headers):
    """GitHub Actions runs omit X-FH-CI-Source; the API then records them as github_actions."""
    assert PARAMS["x-fh-ci-source"]["required"] is False
    route = respx.post(f"{BASE}/api/v2/reports").mock(
        return_value=httpx.Response(201, json={"run": {}, "duplicate": False, "counts": {}})
    )
    upload_report(client, b"<testsuite/>", headers)
    assert "x-fh-ci-source" not in route.calls.last.request.headers
