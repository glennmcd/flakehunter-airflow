#!/usr/bin/env bash
set -euo pipefail
W=$(pwd)
export AIRFLOW_HOME=$W/.airflow AIRFLOW__CORE__DAGS_FOLDER=$W/dags AIRFLOW__CORE__LOAD_EXAMPLES=False
mkdir -p "$AIRFLOW_HOME" "$AIRFLOW__CORE__DAGS_FOLDER"
if ! pgrep -f "airflow standalone" >/dev/null; then
  setsid nohup "$W/.venv/bin/airflow" standalone >"$AIRFLOW_HOME/standalone.log" 2>&1 </dev/null &
fi
