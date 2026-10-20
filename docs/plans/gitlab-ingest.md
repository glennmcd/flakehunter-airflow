# GitLab ingest

**Status:** Draft, for review. No code changes until this is agreed.

This brief extends `flakehunter_ingest` to GitLab CI. A second DAG lists finished GitLab pipelines, collects the JUnit
XML from their jobs and uploads it through FlakeHunter's `POST /api/v2/reports`. Zip extraction, JUnit merge and size
limits are reused unchanged. What is new: a run model shared by both DAGs, a GitLab module, a rule for the run attempt,
a trust check and the configuration.

In FlakeHunter's terms, a GitLab project is a repository with host `gitlab`, and its pipelines are runs with CI source
`gitlab_ci`. The FlakeHunter side is planned in that repo; this brief covers only the DAG.

## FlakeHunter dependencies

This DAG uploads to API v2 only. It needs, from FlakeHunter:

- **Hosts and CI sources** ([CI source adapters](https://github.com/glennmcd/flakehunter/blob/main/docs/plans/ci-source-adapters.md),
  step 2): `repos.host` and `workflow_runs.ci_source`, with runs unique on (repo, CI source, run id, attempt). GitLab
  pipeline ids therefore never collide with GitHub Actions run ids, even if one FlakeHunter repository received both.
- **API v2** ([API v2](https://github.com/glennmcd/flakehunter/blob/main/docs/plans/api-v2.md), step 2):
  `/api/v2/reports` with the optional `X-FH-CI-Source` header, `ciRunId` and `ciSource` in responses, and
  `docs/openapi.v2.json` as the published contract.
- **The `gitlab` and `gitlab_ci` values**, added to `RepoHost`, `CiSource`, `DEFAULT_CI_SOURCE`
  (`gitlab` → `gitlab_ci`) and the database check constraints. Neither FlakeHunter plan adds them; they are a small
  FlakeHunter change of their own, after the two above.
- **Registration**: a GitLab project is registered with `SEED_REPO_HOST=gitlab`, its numeric project id as the
  external id and `path_with_namespace` as the full name (nested paths are accepted from API v2's step 2), and its
  upload token is minted with `TOKEN_REPO_HOST=gitlab`.

On this repo's side, API v2's step 4 moves the existing GitHub DAG to v2 first: `contract/openapi.json` is re-pinned
from FlakeHunter's `docs/openapi.v2.json` (`pin_spec.py` and `check_drift.py` follow the new path), the client is
regenerated, and uploads go to `/api/v2/reports`. The GitLab DAG builds on that client; it never uses v1.

## Shape

```text
discover_pipelines  ──►  upload_pipeline.expand(pipeline)  ──►  summarize
```

A separate DAG, `flakehunter_ingest_gitlab`, with the same schedule, lookback and `flakehunter_upload` pool as the
GitHub DAG. A separate DAG keeps the two systems' connections, failures and backfills apart while sharing all the
upload code.

- **`discover_pipelines`** calls `GET /projects/:id/pipelines?updated_after=…` for each configured project and keeps
  pipelines in a terminal state (`success`, `failed`, `canceled`). Running pipelines are picked up on a later run.
  It applies [Trust](#trust) and returns one descriptor per pipeline.
- **`upload_pipeline`** lists the pipeline's jobs, downloads the artifact of every current (non-retried) job that has
  one, extracts the `.xml` files, merges them into one `<testsuites>` document and uploads it.
- **`summarize`** works as in the GitHub DAG.

## Headers and the run attempt

| Header | Source |
|---|---|
| `X-FH-CI-Source` | `gitlab_ci`, always |
| `X-FH-Run-Id` | `pipeline.id` |
| `X-FH-Run-Attempt` | 1 + number of retried jobs in the pipeline (see below) |
| `X-FH-Sha` | `pipeline.sha` |
| `X-FH-Branch` | `pipeline.ref` |
| `X-FH-Workflow` | `pipeline.name` when set, otherwise omitted |
| `X-FH-Timestamp` | `pipeline.started_at` (single-pipeline endpoint) |
| `X-FH-Report-Key` | `webhook-artifact`, always |

`X-FH-CI-Source` is sent explicitly even though `gitlab_ci` is the default for a `gitlab` repository: a project
registered under the wrong host would otherwise get its runs recorded as the wrong CI system without any error. The
upload key in FlakeHunter is (repository, CI source, run id, attempt, report key); every part comes from GitLab or is
a constant, never from Airflow, so the idempotency rule in `CLAUDE.md` holds.

GitLab has no pipeline-level attempt. Retrying a job keeps the pipeline id and adds a new job, marking the old one
`retried`. If the attempt were always `1`, the first upload would win and every later retry would return `200`
duplicate, losing exactly the same-SHA reruns flaky detection depends on.

The attempt is therefore derived from GitLab's own data: `1 + count(jobs where retried = true)`, from
`GET /projects/:id/pipelines/:id/jobs?include_retried=true`. It is the same on every poll of a finished pipeline and
grows by one with every job retry. Each new attempt uploads the results of the current jobs, which is the GitLab
equivalent of GitHub's "latest attempt".

Results of the retried jobs themselves are not uploaded, as with earlier GitHub attempts. GitLab does keep them, so
this could be added later as a separate attempt per retry; it is out of scope here.

## Artifacts

GitLab stores artifacts per job. The DAG downloads each job's archive with `GET /projects/:id/jobs/:job_id/artifacts`
and merges the XML across jobs, applying the 10 MiB limit per archive and the 11 MiB limit to the merged document.

Projects must publish their JUnit files in the job archive, that is under `artifacts:paths` and not only under
`artifacts:reports:junit`. Whether reports-only JUnit files can be downloaded through the API needs checking (see
[Open questions](#open-questions)). GitLab's parsed `test_report` JSON endpoint is not used: converting it back to XML
would lose detail that FlakeHunter parses.

## Trust

Mirroring the GitHub filter, a pipeline is uploaded only when:

- `pipeline.source` is one of `push`, `merge_request_event`, `schedule` or `web`;
- for `merge_request_event`, the merge request's `source_project_id` equals its `target_project_id`. The merge request
  iid is parsed from `ref` (`refs/merge-requests/<iid>/head`) and fetched with one extra call.

Other sources (`api`, `trigger`, `pipeline`, `parent_pipeline`, `external`, `chat`, …) are counted as skipped.
Fork merge request pipelines that a maintainer runs in the parent project are skipped too: the fork author still
controls the code that produced the artifact.

## Configuration

| Item | Kind | Contents |
|---|---|---|
| `flakehunter_gitlab_projects` | Variable (JSON) | list of numeric GitLab project ids |
| `gitlab_default` | Connection | host = GitLab base URL (gitlab.com or self-hosted), password = token with `read_api` |
| `flakehunter_upload_gitlab_<project_id>` | HTTP Connection | host = FlakeHunter base URL, password = that project's upload token |

Numeric project ids avoid the URL-encoding and nested-path problems of `group/sub/project`, and survive project
renames and transfers. The existing `flakehunter_repos` Variable and GitHub connections are untouched. One GitLab host
per deployment is supported.

## Code changes

These follow the GitHub DAG's move to v2 (see [FlakeHunter dependencies](#flakehunter-dependencies)).

- `src/flakehunter_ingest/run.py`: a provider-neutral `CiRun` (CI source, run id, attempt, sha, branch, workflow,
  started at, upload connection id) with a `headers()` method that builds `RunHeaders`.
- `src/flakehunter_ingest/client.py`: `RunHeaders` gains `ci_source`, sent as `X-FH-CI-Source`; its docstring says
  the values come from the CI run, not specifically the GitHub `workflow_run`. The GitHub path sets
  `github_actions`, which matches what FlakeHunter defaults to, so its uploads stay duplicates of the webhook's.
- `src/flakehunter_ingest/gitlab.py`: HTTP client, pipeline and job listing, attempt derivation, artifact download.
  `download_artifact` moves out of `github.py` into a shared module so both DAGs use the same size-limited stream.
- `src/flakehunter_ingest/trust.py`: an `is_pipeline_trusted` next to the existing check.
- `src/flakehunter_ingest/processrun.py`: split so the "XML files → merge → upload" step takes a `CiRun` and a list
  of zip bytes, independent of the CI system. The GitHub path is moved onto it with no change in behaviour.
- `dags/flakehunter_gitlab_dag.py`: the new DAG.
- `scripts/get_gitlab_fixture.py`: records pipeline, job and artifact fixtures from a real project, like the GitHub
  scripts.

`junit.py`, `safezip.py` and `limits.py` do not change. `_api/` is regenerated only by the v2 re-pin, never by hand.

## Validation

- **Unit tests** (`respx`, recorded fixtures): header mapping from a pipeline payload, including
  `X-FH-CI-Source: gitlab_ci`; attempt derivation with no retries, one retry and retries across several jobs; skipping
  non-terminal pipelines; trust for each source and for same-project and fork merge requests; merging XML from several
  jobs; size limits.
- **Contract:** `tests/test_contract.py` checks that `X-FH-CI-Source` and its values match the pinned v2 spec.
- **Regression:** the existing GitHub tests pass unchanged after the `processrun` split, apart from the new
  `X-FH-CI-Source: github_actions` header.
- **End to end:** in the dev container, `airflow dags test flakehunter_ingest_gitlab` against a local FlakeHunter
  with a `gitlab` repository registered, and a gitlab.com test project. Run the interval twice and expect `201`s then
  duplicates. Retry one job, run again and expect one new `201` for attempt 2 on the same SHA. The run appears in
  FlakeHunter's v2 history with `ciSource: "gitlab_ci"`.

## Open questions

1. Can JUnit files declared only under `artifacts:reports:junit` be downloaded through the jobs API? If yes, the
   "also list them under `artifacts:paths`" requirement goes away.
2. Merged-results pipelines test a merge commit, so `pipeline.sha` is not a commit on the branch. Should those
   pipelines be uploaded, skipped, or tagged by branch?
3. Child pipelines (`parent_pipeline` source) often hold the test jobs in monorepos. Are they needed in the first
   version? Including them means walking bridge jobs and deciding which pipeline id the report belongs to.

## Not in scope

- Results of retried jobs as separate attempts.
- More than one GitLab host per deployment.
- A GitLab webhook or a `gitlab_ci` adapter in FlakeHunter; uploads from this DAG are the only GitLab path.
- FlakeHunter changes, which are planned in that repo.
