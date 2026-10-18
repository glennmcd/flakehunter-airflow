import io
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from flakehunter_ingest.junit import merge_junit

logging.basicConfig(level=logging.DEBUG)
test_logger = logging.getLogger(__name__)

# discover_runs lists completed workflow runs for each configured repository,
# created in the data interval plus a 24-hour lookback
# (GET /repos/{owner}/{repo}/actions/runs?status=completed&created=>=…).
# It drops runs that the webhook would also refuse (see Trust) and returns one
# small descriptor per run.

# test github API
#   test for successful responses from github API
#   test for empty responses from github API
#   test for extra records in the response from github API
#   test if github API only returns approved runs
# test handling of github API errors

# test happy path test with fixture
# test github API results
#   test for list of runs
#   test for required fields existence
#   test parsing of the results
#       test for parsing required fields
#       test for irregular values in required fields
#   test handling of missing fields


def test_extract_junit_combined():
    fixture_path = Path(__file__).parent / "fixtures" / "junit_combined.xml"
    junit_data_combined = ET.parse(fixture_path)

    fixture_path_1 = Path(__file__).parent / "fixtures" / "junit.xml"
    fixture_path_2 = Path(__file__).parent / "fixtures" / "junit2.xml"

    f1: bytes
    f2: bytes
    with open(fixture_path_1, "rb") as f:
        f1 = f.read()
    with open(fixture_path_2, "rb") as f:
        f2 = f.read()

    junit_data = merge_junit({"junit.xml": f1, "junit2.xml": f2})

    junit_data_results = ET.parse(io.BytesIO(junit_data))

    junit_data_combined_top = junit_data_combined.getroot()
    strip_whitespace(junit_data_combined_top)
    assert junit_data_combined_top is not None
    junit_data_top = junit_data_results.getroot()
    strip_whitespace(junit_data_top)
    assert junit_data_top is not None
    junit_data_top_string = ET.tostring(junit_data_top, encoding="utf-8").decode("utf-8")
    junit_data_combined_top_string = ET.tostring(junit_data_combined_top, encoding="utf-8").decode(
        "utf-8"
    )
    a = ET.canonicalize(junit_data_combined_top_string)
    b = ET.canonicalize(junit_data_top_string)
    assert a == b


def strip_whitespace(element):
    """Recursively strip whitespace from element text and tails."""
    if element.text:
        element.text = element.text.strip()
    if element.tail:
        element.tail = element.tail.strip()
    for child in element:
        strip_whitespace(child)
    return element
