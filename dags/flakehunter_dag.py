from __future__ import annotations

import json

# [START example_dynamic_task_mapping]
from datetime import datetime

from airflow.sdk import BaseHook
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
    dag_id="flakehunter_ingest",
    schedule=None,
    start_date=datetime(2022, 3, 4),
    tags=["example"],
):

    @task
    def discover_runs():
        repos = Variable.get("flakehunter_repos", deserialize_json=True)
        github_default = BaseHook.get_connection("github_default").password
        if not github_default:
            raise Exception("github_default connection must have a password set")
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
    def runs_to_upload(found: dict) -> list:
        return found["run_list"]

    @task
    def upload_run(run: GhWorkflowRun):

        connection = BaseHook.get_connection(
            f"flakehunter_upload_{run.repository_owner}_{run.repository_name}"
        )
        process_ghworkflowrun(run, connection.password, connection.host)

        return run

    @task
    def summarize(uploaded: list[GhWorkflowRun], is_found: dict):
        total = len(uploaded) + len(is_found["skipped"])
        print(f"Summary total was {total}")
        return None

    found = discover_runs()
    to_upload = runs_to_upload(found)
    uploaded = upload_run.expand(run=to_upload)
    summarize(uploaded, found)
