from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

from flakehunter_ingest.limits import ArtifactRejected

logger = logging.getLogger(__name__)


def merge_junit(files: dict[str, bytes]) -> bytes:
    """Merge JUnit files into one <testsuites> document. Raises ArtifactRejected on invalid XML."""
    combined = ET.Element("testsuites", name="dag combined")
    for name, content in files.items():
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise ArtifactRejected("artifact contains invalid XML") from e
        if root.tag == "testsuite":
            combined.append(root)  # nest the whole suite
        elif root.tag == "testsuites":
            combined.extend(
                root.findall("testsuite")
            )  # direct children only; nested suites come along
        else:
            logger.warning("Skipping %s: root element is not testsuite(s)", name)
    return ET.tostring(combined, encoding="utf-8", xml_declaration=True)
