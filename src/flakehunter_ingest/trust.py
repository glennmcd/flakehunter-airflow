def is_run_trusted(run):
    return (
        run["event"] in ["push", "pull_request", "merge_group", "schedule", "workflow_dispatch"]
        and run["head_repository"].get("id") == run["repository"].get("id")
    )
