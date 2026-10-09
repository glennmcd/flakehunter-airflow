# Apache Airflow plan (decided 2026-10-08; revised 2026-10-08: separate repo + OpenAPI; section 2 expanded with Codespaces steps)

**Decision (Glenn):** contribute to **Apache Airflow (apache/airflow)** as the Python open-source project. Chosen for job volume (1,612 Dice listings, the most-named non-ML Python project; see `claude/job-leads.md` for the counts) and his past ETL work (Java/SSIS pipelines into SQL Server, OLAP ETL cut from 30 to 2 minutes at Softagon). Fallback: pandas (890 listings, already used in IBApps).

**Repo decision (2026-10-08):** the Airflow pipelines live in a **separate repo, `flakehunter-airflow`** (Python only), not in the FlakeHunter repo. To keep the two from drifting, **FlakeHunter is modified to publish its own API as an OpenAPI spec**, and the Airflow repo consumes that spec.

## Plan

### 1. New repo `flakehunter-airflow` (Python; Session B)
- Pipelines (as in the earlier plan, now consuming the spec instead of hand-written HTTP calls):
  - `flakehunter_ingest` DAG (hourly/daily): for each tracked repo (dynamic task mapping), list completed GitHub Actions runs via the GitHub API, download JUnit XML artifacts, gzip and upload each to FlakeHunter's `POST /api/reports` with the per-repo token and X-FH-* headers. Retries and backfill (catchup) are safe because the API is idempotent. Handles multiple artifacts per run, which the webhook path doesn't (CLAUDE.md scope limit: one artifact per run; webhook processing runs inside the request, SQS was the noted follow-up).
  - `flakehunter_weekly_digest` DAG: call `GET /api/tests/flaky` and send a digest (Slack or email). Covers the roadmap's Slack-alert stretch goal.
- **API client:** generate a typed Python client from FlakeHunter's `openapi.json` (e.g. `openapi-python-client`). Commit the spec copy or pin it to a FlakeHunter release/tag; regenerate on purpose, not implicitly.
- **Drift protection:** a contract test in this repo's CI that fetches or compares the pinned spec against the latest FlakeHunter spec and fails (or opens a reminder) when they differ.
- Secrets via Airflow Connections/Variables, never in code; DAG tests with pytest.
- Python tooling: uv, ruff, pytest; its own CI; a dev container / Codespaces config so Airflow runs without native Windows (see 2A).
- Own Claude Code setup: its own `CLAUDE.md` (Python/Airflow conventions, link to FlakeHunter's API spec), and skills/agents only as needed. FlakeHunter's CLAUDE.md, `/new-endpoint` skill and agents do not apply here.
- **Claude Code context:** `claude --add-dir ../flakehunter` (or `/add-dir` mid-session) gives file access to the FlakeHunter repo, but I believe it does not load that repo's CLAUDE.md, skills or agents; verify with `claude --help`/docs. Prefer pointing Claude at the committed `openapi.json` and the idempotency ADR.
- README links back to FlakeHunter (and vice versa) so the two repos read as one system.

### 2. Running Airflow in GitHub Codespaces
Airflow doesn't run natively on Windows (it needs Linux/WSL2), and Glenn prefers not to run Docker Desktop on his laptop, so both uses run in GitHub Codespaces (a Linux VM with VS Code in the browser). Two separate codespaces:
- **2A** — on `glennmcd/flakehunter-airflow`, to develop and run **his own DAGs**. Lightweight: plain Python install, no Docker.
- **2B** — on **his fork of apache/airflow**, to **contribute** (Breeze, which runs Airflow in Docker inside the codespace).

Codespaces billing: personal accounts get a free monthly allowance of core-hours and storage; beyond it GitHub charges or blocks, depending on your spending limit. Check github.com → Settings → Billing. A 4-core machine uses the allowance twice as fast as a 2-core one. **Stop the codespace when done** (it also auto-stops after an idle timeout, 30 min by default), and delete old ones you no longer need.

#### 2A. Run your own DAGs (`flakehunter-airflow` codespace)
Commands verified against the Airflow quick start (docs version 3.3.2, read 2026-10-08). Airflow 3.x supports Python 3.10–3.14.

1. **Store secrets first (once).** github.com → Settings → Codespaces → Secrets → New secret, with repository access limited to `flakehunter-airflow`. Codespace secrets appear as environment variables, and Airflow reads any variable named `AIRFLOW_CONN_<CONN_ID>` as a Connection, so nothing goes in code:
   - `AIRFLOW_CONN_FLAKEHUNTER_API` — the FlakeHunter API base URL plus the read token (format per the HTTP provider's connection docs; decide in Session B).
   - `AIRFLOW_CONN_GITHUB_DEFAULT` — a GitHub token with read access to Actions artifacts.
   - Per-repo FlakeHunter upload tokens as further secrets or Airflow Variables (`AIRFLOW_VAR_<NAME>`).
2. **Create the codespace.** On the `flakehunter-airflow` repo page: Code → Codespaces → **Create codespace on main**. A 2-core machine is enough for `airflow standalone`.
3. **Install uv** in the terminal:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env   # or open a new terminal
   python --version              # must be 3.10–3.14
   ```
4. **Point Airflow at the repo** (keep Airflow's state out of git; add `.airflow/` and `.venv/` to `.gitignore`):
   ```
   export AIRFLOW_HOME=/workspaces/flakehunter-airflow/.airflow
   export AIRFLOW__CORE__DAGS_FOLDER=/workspaces/flakehunter-airflow/dags
   export AIRFLOW__CORE__LOAD_EXAMPLES=False
   ```
5. **Install Airflow with the matching constraints file** (constraints pin compatible dependency versions; always use them):
   ```
   export AIRFLOW_VERSION=3.3.2
   export PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
   export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
   uv venv .venv && source .venv/bin/activate
   uv pip install "apache-airflow[http,github]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
   ```
   (`http` and `github` install the providers the DAGs use.)

6. **Start Airflow:**
   ```
   airflow standalone
   ```
   It initializes the database, creates an admin user and starts all components.

7. **Open the UI.** In VS Code's **Ports** tab, open port **8080** in the browser. Keep the port **Private** (the default) so only you can reach it. The admin password is printed in the terminal; if not, run `cat $AIRFLOW_HOME/simple_auth_manager_passwords.json.generated`.

8. **Develop and test DAGs** in `dags/`. The scheduler picks up new files after a short delay. For a single run without waiting on the schedule: `airflow dags test flakehunter_ingest`. Unit-test DAG code with pytest.

9. **Make it one click (recommended, Session B):** ask Claude Code to write `.devcontainer/devcontainer.json` that sets the env vars from step 4, installs uv and Airflow (step 5) in `postCreateCommand`, and forwards port 8080. After that, a new codespace is ready without retyping anything.

10. **Stop the codespace when finished.** Note: a codespace is a development environment, not a server. When it stops, the scheduler stops, so DAGs only run on schedule while it's running. Always-on scheduling would need a hosted Airflow (decide later; not needed for the portfolio or for contributing).

#### 2B. Contribute to apache/airflow (Breeze codespace)
Steps from Airflow's beginner contributor quick start ("Option B: Codespaces", read 2026-10-08). The guide gives no machine size; Breeze needs at least 4 GB RAM, 40 GB disk and 2 cores, and a 4-core machine is faster for builds (uses the allowance faster).

1. **Fork** apache/airflow on GitHub to `glennmcd/airflow`.
2. **Create the codespace** on the fork: Code → Codespaces → **New codespace**. Wait for VS Code; a terminal opens.
3. **Install Docker Buildx and Docker Compose:**
   ```
   mkdir -p ~/.docker/cli-plugins

   # Install Docker Buildx
   BUILDX_VERSION=v0.16.2
   curl -SL "https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64" -o ~/.docker/cli-plugins/docker-buildx
   chmod +x ~/.docker/cli-plugins/docker-buildx
   docker buildx version

   # Install Docker Compose v2
   curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)" -o ~/.docker/cli-plugins/docker-compose
   chmod +x ~/.docker/cli-plugins/docker-compose
   docker compose version
   ```
4. **Check Docker:** `docker info`. If it fails, run **Codespaces: Rebuild Container** from the Command Palette, or restart the codespace from the Codespaces dashboard.
5. **Install the contributor tools and start Breeze:**
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv tool install prek
   prek install -f
   prek install -f --hook-type pre-push # for running mypy checks when pushing to repo
   ./scripts/tools/setup_breeze
   uv run dev/ide_setup/setup_vscode.py
   breeze start-airflow
   ```
6. **Create a branch, make the change**, then run the checks before committing:
   ```
   git checkout -b <your-branch-name>
   prek --all-files
   breeze testing core-tests     # or the tests for the provider you changed
   ```
7. **Commit and push** (Source Control sidebar or `git commit` / `git push -u origin <branch>`), then click **Create pull request** when GitHub offers it.
8. **After review:** push updates the same way. To sync with upstream later: `git fetch upstream && git rebase upstream/main && git push --force-with-lease`. A committer merges once CI is green and reviews are approved.
9. **Stop the codespace** between sessions; it keeps your Breeze setup, so restarting is faster than recreating.

### 3. Contributions grow out of the DAGs
First a docs fix or `good first issue` to learn the process, then the providers the DAGs actually use (GitHub, HTTP, Postgres/common-SQL), where bugs or doc gaps he hits become PRs. SQL Server / ODBC providers remain an option for SQL-depth work.

### 4. Resume
- FlakeHunter: add a bullet for publishing the API as an OpenAPI contract generated from the Zod schemas (CI-enforced).
- `flakehunter-airflow`: new bullet for the Airflow pipelines (GitHub Actions → FlakeHunter ingestion with retries, backfill and dynamic task mapping, typed client generated from the OpenAPI spec; weekly digest).
- Later: an Apache Airflow contributor line.
- Only claim what exists in the repos; never invent metrics.

## Why separate repo (trade-offs accepted)
- For: the DAGs are a real external consumer of the public API (proves the API is usable without inside knowledge); Python-only toolchain with no interaction with Bun/Biome; clean, easy-to-scan repo.
- Against: silent drift between repos, weaker Claude Code context, a thinner story per repo. Mitigations: OpenAPI spec + CI staleness check in FlakeHunter, pinned spec + contract test in `flakehunter-airflow`, cross-linked READMEs.
- Escape hatch: if the separate repo becomes a burden, the code can be moved into FlakeHunter under `pipelines/airflow/` (own `pyproject.toml`, path-filtered CI, nested CLAUDE.md).

## Session plan (Claude Code best practice: one task per session, fresh context)
1. **Session A (FlakeHunter repo):** plan mode, then implement step 0, commit (settings deny `git commit`, so Glenn commits), merge to main.
2. **Session B (new `flakehunter-airflow` repo):** fresh session, plan mode to design `flakehunter_ingest` from `openapi.json` and the idempotency ADR; include the `.devcontainer` from 2A step 9. Switch models only at session start or after `/clear` (mid-session switches invalidate the prompt cache).

## Status
- Not started. Next step: Session A (OpenAPI in the FlakeHunter repo), then create the `flakehunter-airflow` repo and start Session B.

Sources: contributing-docs/03a_contributors_quick_start_beginners.rst in apache/airflow; airflow.apache.org/docs/apache-airflow/stable/start.html (both read 2026-10-08).
