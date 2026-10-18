from __future__ import annotations

import copy
import io
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def merge_junit(files: dict[str, bytes]) -> bytes:
    combined_root = ET.Element("testsuites")

    failures_attribute = 0
    num_tests_attribute = 0
    errors_attribute = 0
    amount_of_time_attribute = 0

    for _filename, content in files.items():
        context = ET.iterparse(io.BytesIO(content), events=("start", "end"))
        event, root = next(context)

        for event, elem in context:
            if event == "start" and elem.tag == "testsuite":
                # Process the data
                combined_root.append(copy.deepcopy(elem))
                # CRITICAL: Clear the element to free memory
                elem.clear()
            if event == "end" and elem.tag == "testsuites":
                failures_attribute += int(elem.attrib.get("failures", 0))
                num_tests_attribute += int(elem.attrib.get("tests", 0))
                errors_attribute += int(elem.attrib.get("errors", 0))
                amount_of_time_attribute += float(elem.attrib.get("time", 0))
        # CRITICAL: Clear references from the root element to drop early elements
        combined_root.set("name", "dag combined")
        combined_root.set("failures", str(failures_attribute))
        combined_root.set("tests", str(num_tests_attribute))
        combined_root.set("errors", str(errors_attribute))
        combined_root.set("time", str(amount_of_time_attribute))
        root.clear()
    return ET.tostring(combined_root, encoding="utf-8", xml_declaration=True)
