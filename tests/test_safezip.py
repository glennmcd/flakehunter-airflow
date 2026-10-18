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


def test_safezip_two_part_file(monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_two_part_file")
    monkeypatch.setattr(safezip, "MAX_REPORT_BYTES", 10)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "123456")
        archive.writestr("two.xml", "789012")
    zip_buffer.seek(0)
    with pytest.raises(ArtifactRejected, match="artifact XML exceeds the size limit"):
        read_xml_entries(zip_buffer.getvalue())


def test_safezip_max_file_count(monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_max_file_count")
    monkeypatch.setattr(safezip, "MAX_ZIP_ENTRIES", 1)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "one")
        archive.writestr("two.xml", "<twothreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)
    with pytest.raises(ArtifactRejected, match="artifact zip has too many entries"):
        read_xml_entries(zip_buffer.getvalue())


def test_safezip_skip_non_xml():
    test_logger.debug("Running test_safezip_skip_non_xml")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.zip", "one")
        archive.writestr("two.txt", "<twothreefourfivesizseveneightnineten/>")
        archive.writestr("three.xml", "<threethreefourfivesizseveneightnineten/>")
    zip_buffer.seek(0)

    assert read_xml_entries(zip_buffer.getvalue()) == {
        "three.xml": b"<threethreefourfivesizseveneightnineten/>"
    }


def test_safezip_corrupted():
    test_logger.debug("Running test_safezip_corrupted")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("one.xml", "one")
        archive.writestr("two.xml", "<" + "0" * 150 + "/>")

    zip_buffer.seek(0)
    raw = bytearray(zip_buffer.getvalue())
    i = raw.find(b"two.xml") + 15
    for k in range(i, i + 20):
        raw[k] ^= 0xFF

    zip_buffer = BytesIO(raw)
    with pytest.raises(ArtifactRejected, match="artifact is not a readable zip"):
        read_xml_entries(zip_buffer.getvalue())


def test_safezip_zip_bomb(monkeypatch):
    monkeypatch.setattr(safezip, "MAX_REPORT_BYTES", 1024 * 1024)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("bomb.xml", b"0" * (2 * 1024 * 1024))  # ~2 KB compressed
    with pytest.raises(ArtifactRejected, match="exceeds the size limit"):
        read_xml_entries(buf.getvalue())


def test_safezip_unsafe_entry_name():

    unsafe_names = [
        "../evil.xml",
        "/absolute.xml",
        "C:/windows.xml",
        "normal/../../evil.xml",
        "../notes.txt",
        "/etc/passwd.xml",
    ]
    results = []
    for name in unsafe_names:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            archive.writestr(name, "<testsuite></testsuite>")
        zip_buffer.seek(0)
        try:
            read_xml_entries(zip_buffer.getvalue())
        except ArtifactRejected as e:
            if "artifact contains unsafe entry name" in str(e):
                continue
        results.append(name)

    assert not results, f"{len(results)} unsafe names were not rejected"


@pytest.mark.parametrize("name", [r"dir\x.xml", r"..\..\evil.xml"])
def test_backslash_names_unsafe(name):
    assert not safezip._is_safe_entry_name(name)  # or whatever you named the helper
