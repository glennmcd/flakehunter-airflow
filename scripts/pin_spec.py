"""Re-pin contract/openapi.json to a FlakeHunter tag: `uv run python scripts/pin_spec.py v0.2.0`.

Afterwards run scripts/generate_client.py and update the client wrapper and tests on purpose.
"""

import json
import sys
import urllib.request
from pathlib import Path

REPO = "glennmcd/flakehunter"
ROOT = Path(__file__).resolve().parent.parent


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (fixed https hosts)
        return resp.read()


def main(tag: str) -> int:
    spec_bytes = fetch(f"https://raw.githubusercontent.com/{REPO}/{tag}/docs/openapi.json")
    version = json.loads(spec_bytes)["info"]["version"]
    commit = json.loads(fetch(f"https://api.github.com/repos/{REPO}/commits/{tag}"))["sha"]
    (ROOT / "contract" / "openapi.json").write_bytes(spec_bytes)
    (ROOT / "contract" / "PIN.md").write_text(
        f"""# Pinned FlakeHunter contract

| | |
|---|---|
| Source | https://github.com/{REPO}/blob/{tag}/docs/openapi.json |
| Tag | `{tag}` |
| Commit | `{commit}` |
| `info.version` | `{version}` |

To re-pin: `uv run python scripts/pin_spec.py <tag>`, then
`uv run python scripts/generate_client.py`, and commit both.
""",
        encoding="utf-8",
    )
    print(f"Pinned {tag} ({commit[:7]}), info.version {version}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: pin_spec.py <tag>")
    raise SystemExit(main(sys.argv[1]))
