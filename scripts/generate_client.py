"""Regenerate src/flakehunter_ingest/_api from contract/openapi.json.

Run on purpose: `uv run python scripts/generate_client.py`.

openapi-python-client refuses header parameters typed as date-time, which drops
POST /api/reports entirely. The committed spec stays verbatim; this script strips
`format: date-time` from header parameters in a temporary copy before generating. It also
rejects the application/xml request body, so the copy declares it as a binary body instead;
the wrapper in client.py sends the real Content-Type.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "contract" / "openapi.json"
OUT = ROOT / "src" / "flakehunter_ingest" / "_api"


def main() -> int:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for path in spec["paths"].values():
        for op in path.values():
            for param in op.get("parameters", []):
                if (
                    param.get("in") == "header"
                    and param.get("schema", {}).get("format") == "date-time"
                ):
                    del param["schema"]["format"]
            body = op.get("requestBody")
            if body and "application/xml" in body.get("content", {}):
                body["content"] = {
                    "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
                }

    with tempfile.TemporaryDirectory() as tmp:
        patched = Path(tmp) / "openapi.json"
        patched.write_text(json.dumps(spec), encoding="utf-8")
        gen_out = Path(tmp) / "out"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "openapi_python_client",
                "generate",
                "--path",
                str(patched),
                "--meta",
                "none",
                "--output-path",
                str(gen_out),
                "--overwrite",
            ],
            check=True,
        )
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.copytree(gen_out, OUT)
    print(f"Generated client in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
