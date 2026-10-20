import pytest

from shared.client import RunHeaders, make_client

BASE = "https://fh.example.test"


@pytest.fixture
def client():
    return make_client(BASE, "upload-token")


@pytest.fixture
def headers():
    return RunHeaders(
        run_id=123,
        run_attempt=2,
        sha="a" * 40,
        branch="main",
        workflow="CI",
        timestamp="2026-10-08T12:00:00Z",
    )
