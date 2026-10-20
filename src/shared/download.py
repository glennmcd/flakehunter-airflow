import logging

import httpx

from shared.limits import MAX_ARTIFACT_ZIP_BYTES, ArtifactRejected

logger = logging.getLogger(__name__)


def download_artifact(client: httpx.Client, zip_url: str) -> bytes | None:
    """Stream an artifact archive, refusing it once it passes MAX_ARTIFACT_ZIP_BYTES.

    The client carries the CI system's auth headers. Returns None on an HTTP error status.
    """
    try:
        with client.stream("GET", zip_url) as response:
            response.raise_for_status()  # Raise an exception if the HTTP request failed
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    content_length = int(content_length)
                except ValueError:
                    logger.warning("Invalid content-length header - ignoring")
                    content_length = None
                if content_length is not None and content_length > MAX_ARTIFACT_ZIP_BYTES:
                    raise ArtifactRejected(
                        "Artifact exceeds maximum allowed size in content-length header"
                    )
            running_total = 0
            chunks = []
            for chunk in response.iter_bytes():
                running_total += len(chunk)
                if running_total > MAX_ARTIFACT_ZIP_BYTES:
                    raise ArtifactRejected("Artifact exceeds maximum allowed size in file stream")
                chunks.append(chunk)

            return b"".join(chunks)

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to download artifact zip: {e.response.status_code}")

    return None
