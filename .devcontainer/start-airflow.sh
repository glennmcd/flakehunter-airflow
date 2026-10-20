#!/usr/bin/env bash
# Runs as postAttachCommand: Airflow stays in the foreground of the attach terminal,
# because background processes started from lifecycle hooks are killed when the hook ends.
set -euo pipefail
W=$(pwd)
# Repair .venv if postCreateCommand failed or `uv sync` removed Airflow.
[ -x "$W/.venv/bin/airflow" ] || bash "$W/.devcontainer/install.sh"
export AIRFLOW_HOME=$W/.airflow AIRFLOW__CORE__DAGS_FOLDER=$W/dags AIRFLOW__CORE__LOAD_EXAMPLES=False
mkdir -p "$AIRFLOW_HOME" "$AIRFLOW__CORE__DAGS_FOLDER"
# Tasks pass GhWorkflowRun through XCom; keep the airflow.* default in the list.
export AIRFLOW__CORE__ALLOWED_DESERIALIZATION_CLASSES="airflow.* flakehunter_ingest_github.* flakehunter_ingest_gitlab.* shared.*"
# Show Admin > Configuration in the UI, with sensitive values masked.
export AIRFLOW__API__EXPOSE_CONFIG=True
# In Codespaces the UI is reached through the forwarded URL, not localhost:8080.
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  export AIRFLOW__API__BASE_URL="https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  # Task workers must reach the Execution API directly. Derived from base_url they would go
  # through the forwarded URL, which requires GitHub sign-in, and every task call fails.
  export AIRFLOW__CORE__EXECUTION_API_SERVER_URL="http://localhost:8080/execution/"
fi

# Already serving (e.g. a second window attached): nothing to do.
if curl -sf --max-time 5 http://localhost:8080/api/v2/monitor/health >/dev/null; then
  echo "Airflow is already running on port 8080."
  exit 0
fi

# Not serving: stop leftovers from an earlier start, then start fresh.
PATTERN='[.]venv/bin/airflow|airflow (standalone|scheduler|api.server|dag.processor|triggerer)'
pkill -f "$PATTERN" || true
for _ in $(seq 30); do pgrep -f "$PATTERN" >/dev/null || break; sleep 1; done
pkill -9 -f "$PATTERN" || true

echo "$(date -Is) start-airflow.sh: launching airflow standalone" | tee "$AIRFLOW_HOME/standalone.log"
PYTHONUNBUFFERED=1 "$W/.venv/bin/airflow" standalone 2>&1 | tee -a "$AIRFLOW_HOME/standalone.log"
