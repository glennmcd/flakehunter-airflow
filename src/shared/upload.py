import logging

from shared.client import UploadError, UploadResult, make_client, upload_report
from shared.junit import merge_junit
from shared.limits import ArtifactRejected
from shared.run import CiRun
from shared.safezip import read_xml_entries

logger = logging.getLogger(__name__)


def upload_run_artifacts(
    run: CiRun, zips: list[bytes], upload_url: str, upload_token: str
) -> UploadResult | None:
    """Extract the XML from every archive, merge it into one report and upload it for the run.

    Returns None when an archive is rejected, no archive holds XML, or the upload fails; all are
    logged. An empty report is never uploaded: it would use up the run's upload key.
    """
    xml_data: dict[str, bytes] = {}
    try:
        for index, zip_bytes in enumerate(zips):
            entries = read_xml_entries(zip_bytes)
            if len(zips) > 1:  # keep same-named files from different archives apart
                entries = {f"{index}/{name}": content for name, content in entries.items()}
            xml_data.update(entries)
        if not xml_data:
            logger.error(f"No XML files in the archives of run {run.run_id}; nothing uploaded")
            return None
        suites_file_xml = merge_junit(xml_data)
    except ArtifactRejected as e:
        logger.error(f"Artifact rejected for run {run.run_id}: {e}")
        return None

    api_client = make_client(upload_url, upload_token)
    try:
        upload_result = upload_report(api_client, suites_file_xml, run.headers())
    except UploadError as e:
        logger.error(f"Upload error for run {run.run_id} - {e}")
        return None
    if upload_result.status_code in [200, 201]:
        logger.info(f"Successfully uploaded report for run {run.run_id}")
    else:
        logger.error(f"Failed to upload report for run {run.run_id}")
        logger.error(f"upload_result: {upload_result}")
    return upload_result
