# flakehunter-airflow

Airflow 3 pipeline for [FlakeHunter](https://github.com/glennmcd/flakehunter). The `flakehunter_ingest_github` DAG pulls
JUnit XML artifacts from GitHub Actions runs and uploads them with `POST /api/v2/reports`. It catches runs the
FlakeHunter webhook missed and backfills repositories added later. Uploads are idempotent, so running both paths
never counts a run twice.

The two repos form one system: FlakeHunter owns the API and the contract; this repo is a client of it.

| | |
|---|---|
| FlakeHunter | https://github.com/glennmcd/flakehunter |
| Contract | [`contract/openapi.json`](contract/openapi.json), pinned (see [`contract/PIN.md`](contract/PIN.md)) |
| Design | [`docs/plans/flakehunter-ingest.md`](docs/plans/flakehunter-ingest.md) |

## Status

The GitHub DAG (`dags/flakehunter_github_dag.py`) is in place. A GitLab DAG is planned in
[`docs/plans/gitlab-ingest.md`](docs/plans/gitlab-ingest.md).

Code lives in three packages under `src/`: `shared` (FlakeHunter client, archive and JUnit handling, upload),
`flakehunter_ingest_github`, and later `flakehunter_ingest_gitlab`. `shared` imports neither CI package, and the CI
packages never import each other; `tests/test_layout.py` checks this.

## Develop

Airflow needs Linux. Open the repo in the dev container or a Codespace; it installs Airflow and the project, then starts
`airflow standalone` (see [`docs/plans/airflow-plan.md`](docs/plans/airflow-plan.md)).

```bash
uv sync   # on Windows or CI; in the dev container the project is already installed
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## API client

`src/shared/_api/` is generated from the pinned spec with `openapi-python-client` and committed.
`src/shared/client.py` wraps it for gzip, the size limit and `429` handling. Regenerate on purpose:

```bash
uv run python scripts/generate_client.py
```

The `contract-drift` workflow runs weekly, compares the pin with FlakeHunter's `main`, and opens an issue when
they differ. To adopt a new contract: `uv run python scripts/pin_spec.py <tag>`, regenerate, adjust, commit.

## Configuration

Secrets live in Airflow only.

| Item | Kind | Contents |
|---|---|---|
| `flakehunter_repos` | Variable (JSON) | list of `owner/repo` |
| `github_default` | Connection | GitHub token with `actions:read` |
| `flakehunter_upload_<owner>_<repo>` | HTTP Connection | host = FlakeHunter URL, password = that repository's upload token |

## License

See [LICENSE](LICENSE).
