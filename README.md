# flakehunter-airflow

Airflow 3 pipeline for [FlakeHunter](https://github.com/glennmcd/flakehunter). The `flakehunter_ingest` DAG pulls
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

Scaffold: tooling, the generated API client with its wrapper, contract and drift checks, and CI are in place.
The DAG itself (`github.py`, `junit.py`, `trust.py`, `dags/flakehunter_ingest.py`) is not written yet.

## Develop

Airflow needs Linux. Open the repo in the dev container or a Codespace; it installs Airflow and the project, then starts
`airflow standalone` (see [`docs/plans/airflow-plan.md`](docs/plans/airflow-plan.md)).

```bash
uv sync   # on Windows or CI; in the dev container the project is already installed
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## API client

`src/flakehunter_ingest/_api/` is generated from the pinned spec with `openapi-python-client` and committed.
`src/flakehunter_ingest/client.py` wraps it for gzip, the size limit and `429` handling. Regenerate on purpose:

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
