import re

from flakehunter_ingest_gitlab.pipeline import GlPipeline

TRUSTED_SOURCES = frozenset({"push", "merge_request_event", "schedule", "web"})
MERGE_REQUEST_REF = re.compile(r"refs/merge-requests/(\d+)/head")


def merge_request_iid(pipeline: GlPipeline) -> int | None:
    """The merge request iid of a merge request pipeline, from its ref."""
    match = MERGE_REQUEST_REF.fullmatch(pipeline.ref)
    return int(match.group(1)) if match else None


def is_pipeline_trusted(pipeline: GlPipeline, merge_request: dict | None = None) -> bool:
    """A merge request pipeline is trusted only if the merge request comes from the same project.

    Fork merge requests run in the parent project by a maintainer are not: the fork author still
    controls the code that produced the artifacts.
    """
    if pipeline.source not in TRUSTED_SOURCES:
        return False
    if pipeline.source != "merge_request_event":
        return True
    return (
        merge_request is not None
        and merge_request.get("source_project_id")
        == merge_request.get("target_project_id")
        == pipeline.project_id
    )
