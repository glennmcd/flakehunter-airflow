import os
import zipfile
from pathlib import Path

from flakehunter_ingest.limits import MAX_FILE_COUNT, MAX_RATIO, MAX_TOTAL_SIZE


def safe_zip_check_extract(zip_path: Path, extract_to: Path = Path(".")) -> None:
    with zipfile.ZipFile(zip_path, "r") as archive:
        total_uncompressed_size = 0
        total_compressed_size = 0

        # 1. Check total number of files
        if len(archive.infolist()) > MAX_FILE_COUNT:
            raise ValueError("Too many files in archive. Potential ZIP bomb.")

        for file_info in archive.infolist():
            total_uncompressed_size += file_info.file_size
            total_compressed_size += file_info.compress_size

            # Look for malicious nested extensions (e.g., zip inside zip)
            if file_info.filename.endswith((".zip", ".tar", ".gz")):
                raise ValueError("Nested archives are not allowed.")

        # 2. Check cumulative uncompressed file size
        if total_uncompressed_size > MAX_TOTAL_SIZE:
            raise ValueError("Uncompressed data size exceeds the safe threshold.")

        # 3. Check compression ratio (avoid division by zero)
        if total_compressed_size > 0:
            ratio = total_uncompressed_size / total_compressed_size
            if ratio > MAX_RATIO:
                raise ValueError(f"Abnormal compression ratio ({ratio:.1f}). Potential ZIP bomb.")

        safe_stream_extract(archive, extract_to, max_size=MAX_TOTAL_SIZE)


def safe_stream_extract(archive: zipfile.ZipFile, target_dir: Path, max_size=100_000_000):
    current_total_size = 0
    for member in archive.namelist():
        # Target path safety check (Prevents ZipSlip / Directory Traversal)
        target_path = os.path.abspath(os.path.join(target_dir, member))
        if not target_path.startswith(os.path.abspath(target_dir)):
            raise PermissionError("Directory traversal attempt detected.")

        # Safely read and track file chunks
        with archive.open(member) as source_file:
            # If it's a directory entry, create it and continue
            if member.endswith("/"):
                os.makedirs(target_path, exist_ok=True)
                continue

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as target_file:
                while True:
                    chunk = source_file.read(1024 * 64)  # 64 KB chunks
                    if not chunk:
                        break

                    current_total_size += len(chunk)
                    if current_total_size > max_size:
                        raise ValueError("Extraction aborted: Exceeded maximum allowed size.")

                    target_file.write(chunk)
