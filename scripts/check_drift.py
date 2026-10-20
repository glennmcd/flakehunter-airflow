"""Compare the pinned contract with FlakeHunter's latest published spec.

Exit 0 when identical, 1 when they differ, 2 when the latest spec cannot be fetched.
`uv run python scripts/check_drift.py [--url URL]`. Default is FlakeHunter's API v2 spec on main.
"""

import argparse
import difflib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://raw.githubusercontent.com/glennmcd/flakehunter/main/docs/openapi.v2.json"
PINNED = Path(__file__).resolve().parent.parent / "contract" / "openapi.json"


def canon(raw: str) -> list[str]:
    return json.dumps(json.loads(raw), indent=2, sort_keys=True).splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()
    try:
        with urllib.request.urlopen(args.url, timeout=30) as resp:  # noqa: S310
            latest = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Could not fetch {args.url}: {exc}", file=sys.stderr)
        return 2

    pinned_lines = canon(PINNED.read_text(encoding="utf-8"))
    latest_lines = canon(latest)
    if pinned_lines == latest_lines:
        print("No drift: pinned spec matches the latest FlakeHunter spec.")
        return 0

    diff = list(
        difflib.unified_diff(pinned_lines, latest_lines, "pinned", "latest", lineterm="", n=2)
    )
    print(f"Drift: pinned spec differs from {args.url} ({len(diff)} diff lines).\n")
    print("\n".join(diff[:200]))
    if len(diff) > 200:
        print(f"... {len(diff) - 200} more lines")
    print("\nRe-pin on purpose: see contract/PIN.md.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
