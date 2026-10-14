#!/usr/bin/env bash
set -euo pipefail
W=$(pwd)
# Repair .venv if postCreateCommand failed or `uv sync` removed Airflow.
[ -x "$W/.venv/bin/airflow" ] || bash "$W/.devcontainer/install.sh"
export AIRFLOW_HOME=$W/.airflow AIRFLOW__CORE__DAGS_FOLDER=$W/dags AIRFLOW__CORE__LOAD_EXAMPLES=False
mkdir -p "$AIRFLOW_HOME" "$AIRFLOW__CORE__DAGS_FOLDER"

# Already serving: nothing to do.
curl -sf --max-time 5 http://localhost:8080/api/v2/monitor/health >/dev/null && exit 0

# Not serving: stop leftovers from an earlier start, then start fresh.
PATTERN='[.]venv/bin/airflow|airflow (standalone|scheduler|api.server|dag.processor|triggerer)'
pkill -f "$PATTERN" || true
for _ in $(seq 30); do pgrep -f "$PATTERN" >/dev/null || break; sleep 1; done
pkill -9 -f "$PATTERN" || true

setsid nohup "$W/.venv/bin/airflow" standalone >"$AIRFLOW_HOME/standalone.log" 2>&1 </dev/null &
