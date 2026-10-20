"""The import rule from docs/plans/gitlab-ingest.md ("Package layout").

Each CI package imports `shared`; `shared` imports no CI package; CI packages never import each
other. Nothing else on Airflow's sys.path may be called `shared`.
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CI_PACKAGES = ["flakehunter_ingest_github", "flakehunter_ingest_gitlab"]


def imported_packages(package: str) -> set[str]:
    found: set[str] = set()
    for path in (SRC / package).rglob("*.py"):
        if "_api" in path.relative_to(SRC).parts:
            continue  # generated; relative imports only
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def test_shared_imports_no_ci_package():
    assert imported_packages("shared").isdisjoint(CI_PACKAGES)


@pytest.mark.parametrize("package", CI_PACKAGES)
def test_ci_packages_do_not_import_each_other(package: str):
    if not (SRC / package).is_dir():
        pytest.skip(f"{package} does not exist yet")
    others = set(CI_PACKAGES) - {package}
    assert imported_packages(package).isdisjoint(others)


@pytest.mark.parametrize("folder", ["dags", "plugins"])
def test_nothing_shadows_shared(folder: str):
    assert not (ROOT / folder / "shared").exists()
    assert not (ROOT / folder / "shared.py").exists()
