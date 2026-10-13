from __future__ import annotations

# [START example_dynamic_task_mapping]
from datetime import datetime
from tkinter import Variable
import json
from flakehunter_ingest.github import get_github_repo_run_url, get_runs_from_github, get_list_of_runs

from airflow.sdk import DAG, task

with DAG(
    dag_id="example_dynamic_task_mapping",
    schedule=None,
    start_date=datetime(2022, 3, 4),
    tags=["example"],
):

    @task
    def discover_runs(values):
        repos = Variable.get("flakehunter_repos", deserialize_json=True)
        github_default = Variable.get("github_default", deserialize_json=True)
        if repos == []:
            raise Exception(f"flakehunter_repos needs a list of owner/repos")
        run_list = []
        for a in repos:
            owner, repo = a.split("/")
            url = get_github_repo_run_url(owner, repo)
            runs_json = get_runs_from_github(url,github_default)
            run_list.extend(get_list_of_runs(runs_json))

        return run_list

    @task
    def upload_run(x: json):
        
        return x

    @task
    def summarize(values):
        total = sum(values)
        print(f"Summary total was {total}")
        return None

upload_run().expand(discover_runs())>>summarize()
