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
    qualify_discovered_runs,
)
from flakehunter_ingest.processrun import process_ghworkflowrun

with DAG(
    dag_id="example_dynamic_task_mapping",
    schedule=None,
    start_date=datetime(2022, 3, 4),
    tags=["example"],
):

    @task
    def discover_runs():
        repos = Variable.get("flakehunter_repos", deserialize_json=True)
        github_default = Variable.get("github_default", deserialize_json=True)

        if repos == []:
            raise Exception("flakehunter_repos needs a list of owner/repos")
        run_list = []
        skipped = []
        for a in repos:
            owner, repo = a.split("/")
            url = get_github_repo_run_url(owner, repo)
            with get_http_client_github(github_default) as client:
                runs_data = get_resp_from_githubapi(client, url)
                runs = get_list_of_runs(json.loads(runs_data))
                valid_runs, skipped_runs = qualify_discovered_runs(runs)
                run_list.extend(valid_runs)
                skipped.extend(skipped_runs)

        return {"run_list": run_list, "skipped": skipped}

    @task
    def upload_run(run: GhWorkflowRun):

        upload_json = Variable.get(
            f"flakehunter_upload_{run.repository_owner}_{run.repository_name}", deserialize_json=True
        )

        process_ghworkflowrun(run, upload_json.get("token"), upload_json.get("url"))

        return run

    @task
    def summarize(uploaded: list[GhWorkflowRun], skipped: list[GhWorkflowRun]):
        total = len(uploaded) + len(skipped)
        print(f"Summary total was {total}")
        return None


found = discover_runs()
uploaded = upload_run.expand(run=found["run_list"])
summarize(uploaded, found["skipped"])
