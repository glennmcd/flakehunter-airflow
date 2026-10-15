from __future__ import annotations

import json

# [START example_dynamic_task_mapping]
from datetime import datetime

from airflow.sdk import DAG, Variable, task

from flakehunter_ingest.ghworkflowrun import GhWorkflowRun
from flakehunter_ingest.github import (
    get_github_repo_run_url,
    get_http_client_github,
    get_list_of_runs,
    get_resp_from_githubapi,
)
from flakehunter_ingest.processrun import process_ghworkflowrun

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
            raise Exception("flakehunter_repos needs a list of owner/repos")
        run_list = []
        for a in repos:
            owner, repo = a.split("/")
            url = get_github_repo_run_url(owner, repo)
            with get_http_client_github(github_default) as client:
                runs_data = get_resp_from_githubapi(client, url)
                run_list.extend(get_list_of_runs(json.loads(runs_data)))

        return run_list

    @task
    def upload_run(x: GhWorkflowRun):

        upload_json = Variable.get(
            f"flakehunter_upload_{x.repository_owner}_{x.repository_name}", deserialize_json=True
        )

        process_ghworkflowrun(x, upload_json.get("token"), upload_json.get("url"))

        return x

    @task
    def summarize(values):
        total = sum(values)
        print(f"Summary total was {total}")
        return None


upload_run().expand(discover_runs()) >> summarize()
