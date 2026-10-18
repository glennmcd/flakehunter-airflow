import io
import logging
import zipfile
from pathlib import Path

from flakehunter_ingest.limits import MAX_REPORT_BYTES, MAX_ZIP_ENTRIES, ArtifactRejected

CHUNK_LIMIT = 64 * 1024  # 64 KB chunks

logger = logging.getLogger(__name__)


def read_xml_entries(zip_bytes: bytes) -> dict[str, bytes]:
    xml_entries: dict[str, bytes] = {}
    total = 0
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as archive:
            info_list = archive.infolist()
            if len(info_list) > MAX_ZIP_ENTRIES:
                raise ArtifactRejected("artifact zip has too many entries")
            for file_info in info_list:
                chunks = []
                if file_info.is_dir() or not file_info.filename.lower().endswith(".xml"):
                    continue
                
                with archive.open(file_info) as file:
                    # := checks for non-empty chunk, Read in 64 KB chunks
                    while chunk := file.read(CHUNK_LIMIT):
                        total += len(chunk)
                        if total > MAX_REPORT_BYTES:
                            raise ArtifactRejected("artifact XML exceeds the size limit")
                        chunks.append(chunk)
                xml_entries[file_info.filename] = b"".join(chunks)
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError) as e:
        raise ArtifactRejected("artifact is not a readable zip") from e
    return xml_entries
