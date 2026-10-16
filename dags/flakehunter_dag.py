from __future__ import annotations

# [START example_dynamic_task_mapping]
from dataclasses import asdict
from datetime import datetime

from airflow.sdk import DAG, BaseHook, Variable, task

from flakehunter_ingest.ghworkflowrun import GhWorkflowRun
from flakehunter_ingest.github import (
    get_github_repo_run_url,
    get_http_client_github,
    get_list_of_runs,
    get_resp_from_githubapi,
    qualify_discovered_runs,
    validate_repos,
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
        repos_str = Variable.get("flakehunter_repos", deserialize_json=False)
        repos = validate_repos(repos_str)
        github_default = BaseHook.get_connection("github_pat").password
        if not github_default:
            raise Exception("github_default connection must have a password set")
        if repos == []:
            raise Exception("flakehunter_repos needs a list of owner/repos")
        run_list: list[GhWorkflowRun] = []
        skipped: list[GhWorkflowRun] = []
        for a in repos:
            url = get_github_repo_run_url(a.owner, a.repo)
            with get_http_client_github(github_default) as client:
                runs_data = get_resp_from_githubapi(client, url)
                runs = get_list_of_runs(runs_data)
                valid_runs, skipped_runs = qualify_discovered_runs(runs)
                run_list.extend(valid_runs)
                skipped.extend(skipped_runs)

        return {"run_list": [asdict(r) for r in run_list], "skipped": [asdict(r) for r in skipped]}

    @task
    def runs_to_upload(found: dict) -> list[dict]:
        return found["run_list"]

    @task
    def upload_run(run_data: dict):
        workflow_run = GhWorkflowRun(**run_data)
        connection = BaseHook.get_connection(
            f"flakehunter_upload_{workflow_run.repository_owner}_{workflow_run.repository_name}"
        )
        if not connection.password:
            raise Exception(
                f"Connection flakehunter_upload_{workflow_run.repository_owner}_{workflow_run.repository_name} \
                    must have a password set"
            )
        if not connection.host:
            raise Exception(
                f"Connection flakehunter_upload_{workflow_run.repository_owner}_{workflow_run.repository_name} \
                    must have a host set"
            )
        process_ghworkflowrun(workflow_run, connection.password, connection.host)

        return workflow_run

    @task
    def summarize(uploaded: list[dict], is_found: dict):
        total = len(uploaded) + len(is_found["skipped"])
        print(f"Summary total was {total}")
        return None

    found = discover_runs()
    to_upload = runs_to_upload(found)
    uploaded = upload_run.expand(run_data=to_upload)
    summarize(uploaded, found)
