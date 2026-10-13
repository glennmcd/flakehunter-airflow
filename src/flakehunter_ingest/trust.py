from flakehunter_ingest.ghworkflowrun import GhWorkflowRun


def is_run_trusted(run: GhWorkflowRun):
    return (
        run.event in ["push", "pull_request", "merge_group", "schedule", "workflow_dispatch"]
        and run.head_repository_id == run.repository_id
    )
