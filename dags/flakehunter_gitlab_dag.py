from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from airflow.sdk import DAG, BaseHook, Variable, task

from flakehunter_ingest_gitlab.gitlab import (
    get_http_client_gitlab,
    list_pipelines,
    qualify_pipelines,
    validate_projects,
)
from flakehunter_ingest_gitlab.pipeline import GlPipeline
from flakehunter_ingest_gitlab.processpipeline import process_pipeline

LOOKBACK = timedelta(days=7)  # discovery window only; never part of a header


def gitlab_connection() -> tuple[str, str]:
    connection = BaseHook.get_connection("gitlab_default")
    if not connection.host or not connection.password:
        raise Exception("gitlab_default connection must have a host and a password set")
    return connection.host, connection.password


with DAG(
    dag_id="flakehunter_ingest_gitlab",
    schedule=None,
    start_date=datetime(2022, 3, 4),
    tags=["example"],
):

    @task
    def discover_pipelines():
        projects_str = Variable.get("flakehunter_gitlab_projects", deserialize_json=False)
        projects = validate_projects(projects_str)
        if projects == []:
            raise Exception("flakehunter_gitlab_projects needs a list of numeric project ids")
        host, token = gitlab_connection()
        updated_after = datetime.now(UTC) - LOOKBACK
        pipelines: list[GlPipeline] = []
        skipped: list[GlPipeline] = []
        with get_http_client_gitlab(host, token) as client:
            for project_id in projects:
                found = list_pipelines(client, project_id, updated_after)
                valid, rest = qualify_pipelines(client, found)
                pipelines.extend(valid)
                skipped.extend(rest)

        return {
            "pipelines": [asdict(p) for p in pipelines],
            "skipped": [asdict(p) for p in skipped],
        }

    @task
    def pipelines_to_upload(found: dict) -> list[dict]:
        return found["pipelines"]

    @task
    def upload_pipeline(pipeline_data: dict):
        pipeline = GlPipeline(**pipeline_data)
        con_name = f"flakehunter_upload_gitlab_{pipeline.project_id}"
        connection = BaseHook.get_connection(con_name)
        if not connection.password:
            raise Exception(f"Connection {con_name} must have a password set")
        if not connection.host:
            raise Exception(f"Connection {con_name} must have a host set")
        host, token = gitlab_connection()
        with get_http_client_gitlab(host, token) as client:
            process_pipeline(client, pipeline, connection.password, connection.host)

        return pipeline_data

    @task
    def summarize(uploaded: list[dict], is_found: dict):
        total = len(uploaded) + len(is_found["skipped"])
        print(f"Summary total was {total}")
        return None

    found = discover_pipelines()
    to_upload = pipelines_to_upload(found)
    uploaded = upload_pipeline.expand(pipeline_data=to_upload)
    summarize(uploaded, found)
