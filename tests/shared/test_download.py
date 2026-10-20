import io
import zipfile

import httpx
import pytest
import respx

from shared import download
from shared.download import download_artifact
from shared.limits import ArtifactRejected


@respx.mock
def test_content_length_too_large(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "MAX_ARTIFACT_ZIP_BYTES", 1)

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
        httpx.Client() as client,
    ):
        download_artifact(client, "https://example.com/artifacts")


@respx.mock
def test_content_body_too_large(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "MAX_ARTIFACT_ZIP_BYTES", 1)

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
        httpx.Client() as client,
    ):
        download_artifact(client, "https://example.com/artifacts")


@respx.mock
def test_content_length_invalid_is_ignored():
    body = b"zip bytes"
    respx.get("https://example.com/artifacts").mock(
        return_value=httpx.Response(200, content=body, headers={"Content-Length": "abc"})
    )
    with httpx.Client() as client:
        assert download_artifact(client, "https://example.com/artifacts") == body


@respx.mock
def test_content_returns_404():

    respx.get("https://example.com/artifacts").mock(return_value=httpx.Response(404))
    with httpx.Client() as client:
        assert download_artifact(client, "https://example.com/artifacts") is None
