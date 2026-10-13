from __future__ import annotations

import logging
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


def get_combined_artifact(fixture_paths: list[Path]) -> Path:

    combined_root = ET.Element("testsuites")
    combined_tree = ET.ElementTree(combined_root)
    failures_attribute = 0
    num_tests_attribute = 0
    errors_attribute = 0
    amount_of_time_attribute = 0
    for fixture_path in fixture_paths:
        with open(fixture_path, encoding="utf-8") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            failures_attribute += int(root.attrib.get("failures", 0))
            num_tests_attribute += int(root.attrib.get("tests", 0))
            errors_attribute += int(root.attrib.get("errors", 0))
            amount_of_time_attribute += float(root.attrib.get("time", 0))
            for child in root:
                combined_root.append(child)
    combined_path = Path(tempfile.gettempdir()) / "combined_junit.xml"
    combined_root.set("name", "dag combined")
    combined_root.set("failures", str(failures_attribute))
    combined_root.set("tests", str(num_tests_attribute))
    combined_root.set("errors", str(errors_attribute))
    combined_root.set("time", str(amount_of_time_attribute))
    combined_tree.write(combined_path, encoding="utf-8", xml_declaration=True)
    return combined_path


def extract_testsuite(zip_path: Path) -> list[ET.ElementTree[ET.Element]] | None:
    # ...existing code...:
    if not os.path.exists(zip_path):
        logger.error(f"Zip file does not exist: {zip_path}")
        return None
    try:
        extracted_trees = []
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".xml"):
                    with zip_ref.open(file_name) as f:
                        tree = ET.parse(f)
                        extracted_trees.append(tree)
        return extracted_trees if extracted_trees else None
    except Exception as e:
        logger.error(f"Failed to extract testsuite from zip: {zip_path} {e}")
        return None
