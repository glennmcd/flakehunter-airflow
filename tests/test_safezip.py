import logging
import zipfile
from pathlib import Path

import pytest

import flakehunter_ingest.safezip as safezip
from flakehunter_ingest.safezip import safe_zip_check_extract

logging.basicConfig(level=logging.DEBUG)
test_logger = logging.getLogger(__name__)


def test_safezip_basic(tmp_path):
    test_logger.debug("Running test_safezip_basic")
    zip_path = tmp_path / "basic_test.zip"
    archive: zipfile.ZipFile
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("one.txt", "one")

    safe_zip_check_extract(zip_path, tmp_path)
    extracted_file = tmp_path / "one.txt"
    assert extracted_file.exists()
    assert extracted_file.read_text() == "one"


def test_safezip_max_file_size(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip_max_file_size")
    monkeypatch.setattr(safezip, "MAX_REPORT_BYTES", 10)

    zip_path = tmp_path / "large_files.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("one.txt", "one")
        archive.writestr("two.txt", "twothreefourfivesizseveneightnineten")

    with pytest.raises(ValueError, match="Uncompressed data size exceeds the safe threshold."):
        safe_zip_check_extract(zip_path, tmp_path)


def test_safezip_max_file_count(tmp_path, monkeypatch: pytest.MonkeyPatch):
    test_logger.debug("Running test_safezip")
    monkeypatch.setattr(safezip, "MAX_ZIP_ENTRIES", 1)

    zip_path = Path(__file__).parent / "fixtures" / "test_zip_file.zip"
    try:
        safe_zip_check_extract(zip_path, tmp_path)
    except ValueError as e:
        test_logger.debug(f"Validate override number of files: {e}")
        assert True
        return
    # Add your test logic here
    raise AssertionError("Expected ValueError due to max file count")


def test_safezip_rejects_too_many_files(tmp_path, monkeypatch):
    monkeypatch.setattr(safezip, "MAX_ZIP_ENTRIES", 1)

    zip_path = tmp_path / "many_files.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("one.txt", "one")
        archive.writestr("two.txt", "two")

    with pytest.raises(ValueError, match="Too many files"):
        safezip.safe_zip_check_extract(zip_path, tmp_path / "out")
