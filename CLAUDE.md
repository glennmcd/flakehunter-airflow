# flakehunter-airflow

Airflow 3 DAGs that pull JUnit XML from GitHub Actions and GitLab CI and upload it to
[FlakeHunter](https://github.com/glennmcd/flakehunter). Design: `docs/plans/flakehunter-ingest.md`,
`docs/plans/gitlab-ingest.md`.

This repo is separate from FlakeHunter. FlakeHunter's `CLAUDE.md`, `/new-endpoint` skill and agents do not
apply here.

## FlakeHunter context

- **Contract:** `contract/openapi.json`, a pinned copy of FlakeHunter's `docs/openapi.v2.json`, the API v2 contract
  (see `contract/PIN.md`). Read this file, not the FlakeHunter source tree.
- **Idempotency:** [ADR 0005](https://github.com/glennmcd/flakehunter/blob/main/docs/decisions/0005-upload-api-xml-and-headers.md);
  tokens: [ADR 0006](https://github.com/glennmcd/flakehunter/blob/main/docs/decisions/0006-read-token-and-upload-tokens.md).
- `claude --add-dir ../flakehunter` (or `/add-dir`) gives file access to that checkout only. Project instructions,
  skills and agents of an added directory are not relied on here. Prefer the committed spec and ADRs.

## Commands

| | |
|---|---|
| Install | `uv sync` |
| Test | `uv run pytest` |
| Lint / format | `uv run ruff check .` / `uv run ruff format .` |
| Regenerate client | `uv run python scripts/generate_client.py` |
| Re-pin spec | `uv run python scripts/pin_spec.py <tag>` |
| Check drift | `uv run python scripts/check_drift.py` |

Airflow does not run natively on Windows. Use the dev container / Codespaces (`.devcontainer/`); it installs
Airflow (with the official constraints file) and this project into `.venv`, which is on `PATH`, and starts
`airflow standalone`. In the container, run `pytest` / `ruff` directly; `uv sync` or `uv run` would remove Airflow
from `.venv` unless given `--inexact` / `--no-sync`.

## Conventions

- Python 3.12, `uv`, `ruff` (line length 100), `pytest`. Type hints on public functions.
- Logic is plain Python in `src/`, testable without Airflow. `dags/` only wires tasks together.
- Packages: `shared` (no CI-system code), `flakehunter_ingest_github`, `flakehunter_ingest_gitlab`. Each CI package
  imports `shared`; `shared` imports neither; the CI packages never import each other (`tests/test_layout.py`).
- `src/shared/_api/` is generated and committed. Never edit it by hand; CI fails if it is stale.
  Use `client.py` (the wrapper) for everything the generator cannot express.
- The spec is pinned and changed on purpose: re-pin, regenerate, update the wrapper and tests in one commit.
  The weekly `contract-drift` workflow opens an issue when FlakeHunter's spec moves.
- **Idempotency:** every `X-FH-*` value comes from the CI run (GitHub `workflow_run`, GitLab pipeline and its
  jobs) or is a constant. Never use `dag_run.run_id`, the logical date or the try number in a header. Report key
  is always `webhook-artifact`. GitLab uploads always send `X-FH-CI-Source: gitlab_ci`; GitHub uploads send none.
- **Secrets:** only through Airflow Connections and Variables (`github_default`,
  `flakehunter_upload_<owner>_<repo>`, `flakehunter_repos`, `gitlab_default`,
  `flakehunter_upload_gitlab_<project_id>`, `flakehunter_gitlab_projects`). Never in code, DAG files, logs, XCom or
  committed config. Do not print tokens or full request headers.
- DAG tests use pytest with `respx` mocks. No network in unit tests.
- Conventional Commits. Work directly on `main`.
