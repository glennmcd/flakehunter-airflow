#!/usr/bin/env bash
set -euo pipefail
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
AIRFLOW_VERSION=3.3.2
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
uv venv --allow-existing .venv
uv pip install --python .venv/bin/python "apache-airflow[http,github]==${AIRFLOW_VERSION}" -e . pytest respx ruff \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
