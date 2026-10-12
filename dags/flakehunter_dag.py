
from __future__ import annotations

# [START example_dynamic_task_mapping]
from datetime import datetime

from airflow.sdk import DAG, task, task_group

with DAG(
    dag_id="example_dynamic_task_mapping", schedule=None, start_date=datetime(2022, 3, 4), tags=["example"]
):

    
    @task
    def discover_runs(values):
        return values

    @task
    def upload_run(x: int):
        return x
    
    @task
    def summarize(values):
        total = sum(values)
        print(f"Summary total was {total}")