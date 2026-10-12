import json
import os
from pathlib import Path

import httpx


# use export GITHUB_TOKEN=your_token_here in bash
def main() -> int:
    url = "https://api.github.com/repos/glennmcd/flakehunter-test-fixture/actions/runs"
    YOUR_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {YOUR_GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    print(headers)
    with httpx.Client(headers=headers, timeout=10) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        fixture_path = (
            Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "github_list_runs.json"
        )
        fixture_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
