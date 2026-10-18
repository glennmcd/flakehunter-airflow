import logging
import zipfile
from io import BytesIO

import pytest

import flakehunter_ingest.safezip as safezip
from flakehunter_ingest.limits import ArtifactRejected
from flakehunter_ingest.safezip import read_xml_entries

logging.basicConfig(level=logging.DEBUG)
test_logger = logging.getLogger(__name__)


def test_safezip_basic():
    test_logger.debug("Running test_safezip_basic")

    zip_buffer = BytesIO()
    archive: zipfile.ZipFile
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "one")
    zip_buffer.seek(0)
    xml_entries = read_xml_entries(zip_buffer.getvalue())

    assert "one.xml" in xml_entries
    assert xml_entries["one.xml"] == b"one"


def test_safezip_max_file_size(monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_max_file_size")
    monkeypatch.setattr(safezip, "MAX_REPORT_BYTES", 10)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "one")
        archive.writestr("two.xml", "<twothreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)
    with pytest.raises(ArtifactRejected, match="artifact XML exceeds the size limit"):
        read_xml_entries(zip_buffer.getvalue())


def test_safezip_max_file_count(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_max_file_count")
    monkeypatch.setattr(safezip, "MAX_ZIP_ENTRIES", 1)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "one")
        archive.writestr("two.xml", "<twothreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)
    with pytest.raises(ArtifactRejected, match="artifact zip has too many entries"):
        read_xml_entries(zip_buffer.getvalue())


def test_safezip_skip_non_xml(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_skip_non_xml")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.zip", "one")
        archive.writestr("two.txt", "<twothreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)
    with pytest.raises(ArtifactRejected, match="artifact zip has too many entries"):
        assert read_xml_entries(zip_buffer.getvalue()) == {}


def test_safezip_path_issue(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_path_issue")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("../../evil.xml", "one")

    zip_buffer.seek(0)
    output = read_xml_entries(zip_buffer.getvalue())
    assert output["../../evil.xml"] == b""


def test_safezip_corrupted(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_skip_non_xml")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.zip", "one")
        archive.writestr("two.txt", "<twothreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)

    # set the 20th element from the end of zip_buffer to 0x00 to corrupt the zip
    buffer = bytearray(zip_buffer.getvalue())
    buffer[len(buffer) - 20] = 0x00

    zip_buffer = BytesIO(buffer)
    with pytest.raises(ArtifactRejected, match="artifact is not a readable zip"):
        assert read_xml_entries(zip_buffer.getvalue()) == {}
