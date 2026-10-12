import json
import os
from pathlib import Path

import httpx

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


# use export GITHUB_TOKEN=your_token_here in bash
def download_github_artifact_zip() -> int:
    url = "https://api.github.com/repos/glennmcd/flakehunter-test-fixture/actions/artifacts/11375895934/zip"
    YOUR_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {YOUR_GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    print(headers)
    with httpx.Client(headers=headers, timeout=20, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()

        fixture_path = FIXTURES_DIR / "github_artifact.zip"
        fixture_path.write_bytes(response.content)
    return 0


def download_github_artifact():
    url = "https://api.github.com/repos/glennmcd/flakehunter-test-fixture/actions/runs/37382066142/artifacts"
    YOUR_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {YOUR_GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    print(headers)
    with httpx.Client(headers=headers, timeout=10, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        fixture_path = FIXTURES_DIR / "artifact_spec.json"
        fixture_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    download_github_artifact_zip()
    download_github_artifact()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
