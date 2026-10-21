# GitLab ingest

**Status:** Implemented against FlakeHunter `v0.5.0` (spec 2.1.0), with unit tests; the end-to-end run in
[Validation](#validation) is still to do. Where the code settled details this brief left open, see
[Implementation notes](#implementation-notes).

This brief extends the ingest to GitLab CI. A second DAG lists finished GitLab pipelines, collects the JUnit XML from
their jobs and uploads it through FlakeHunter's `POST /api/v2/reports`. The code is split into three packages: one per
CI system and a `shared` package for everything that does not depend on one (see [Package layout](#package-layout)).
Zip extraction, JUnit merge and size limits are reused unchanged. What is new: a run model shared by both DAGs, a GitLab
package, a rule for the run attempt, a trust check and the configuration.

In FlakeHunter's terms, a GitLab project is a repository with host `gitlab`, and its pipelines are runs with CI source
`gitlab_ci`. The FlakeHunter side is planned in that repo; this brief covers only the DAG.

## FlakeHunter dependencies

This DAG uploads to API v2 only, through the client generated from `contract/openapi.json`. The GitHub DAG already
uses it: the contract is pinned at FlakeHunter `v0.3.0` (`docs/openapi.v2.json`, `info.version` 2.0.0, see
`contract/PIN.md`). That pin already provides:

- `POST /api/v2/reports` with the optional `X-FH-CI-Source` header. Uploads are idempotent on (CI source, run id,
  attempt, report key) within the token's repository, so GitLab pipeline ids never collide with GitHub Actions run
  ids, even if one FlakeHunter repository received both.
- `run.ciRunId` and `run.ciSource` in the `200`/`201` responses, and `host` on `GET /api/v2/repos`.

What it does not provide yet is the GitLab values. In `v0.3.0` the `X-FH-CI-Source` and `ciSource` enums contain
only `github_actions`, and `host` only `github`. The DAG needs, from FlakeHunter:

- **The `gitlab` and `gitlab_ci` values**, added to `RepoHost`, `CiSource`, `DEFAULT_CI_SOURCE`
  (`gitlab` → `gitlab_ci`), the database check constraints and the published `docs/openapi.v2.json`. This is a
  small FlakeHunter change of its own, released under a new tag.
- **Registration**: a GitLab project is registered with `SEED_REPO_HOST=gitlab`, its numeric project id as the
  external id and `path_with_namespace` as the full name (nested paths are accepted by API v2), and its upload token
  is minted with `TOKEN_REPO_HOST=gitlab`.

On this repo's side, after the restructure (see [Code changes](#code-changes)), the next step is a re-pin to that tag (`uv run python scripts/pin_spec.py <tag>`, then
`generate_client.py`), committed with the wrapper and test updates as one change. Until then the generated client
and `tests/test_contract.py` reject `gitlab_ci`, so no GitLab code can land before the re-pin.

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

The v2 contract constrains the values:

- `X-FH-Run-Id` is a positive integer up to 2^53 − 1; GitLab pipeline ids fit.
- `X-FH-Sha` must be 40 lowercase hex characters. Projects using SHA-256 object format do not match; their pipelines
  are counted as skipped, not uploaded.
- `X-FH-Timestamp` is RFC 3339. `pipeline.started_at` is null for a pipeline canceled before any job started; the
  header is then omitted. The contract gives no default for it; what FlakeHunter records then needs checking (see
  [Open questions](#open-questions)).
- Without `X-FH-Workflow`, FlakeHunter records the workflow as `upload`.

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

## Package layout

```text
src/
  shared/                       no CI-system code; imports neither package below
    _api/                       generated FlakeHunter client (moved from flakehunter_ingest/_api)
    client.py                   RunHeaders, upload_report, gzip, size limit, 429 handling
    run.py                      CiRun: the provider-neutral run
    upload.py                   zip bytes → XML files → merge → upload, for any CiRun
    download.py                 size-limited artifact stream (moved out of github.py)
    junit.py  safezip.py  limits.py
  flakehunter_ingest_github/    today's flakehunter_ingest, renamed
    github.py  ghworkflowrun.py  ghartifactspec.py
    trust.py                    is_run_trusted
    processrun.py               GhWorkflowRun → CiRun + artifact zips → shared.upload
  flakehunter_ingest_gitlab/
    gitlab.py                   HTTP client, pipeline and job listing, attempt derivation
    pipeline.py                 GlPipeline, parsed from the API like GhWorkflowRun
    trust.py                    is_pipeline_trusted
    processpipeline.py          GlPipeline → CiRun + job archives → shared.upload
dags/
  flakehunter_github_dag.py     dag_id flakehunter_ingest_github; imports flakehunter_ingest_github
  flakehunter_gitlab_dag.py     dag_id flakehunter_ingest_gitlab; imports flakehunter_ingest_gitlab
```

The dependency rule is one-way: each CI package imports `shared`, `shared` imports neither, and the two CI packages
never import each other. A GitLab change then cannot break the GitHub DAG except through `shared`, whose tests cover
both. `tests/test_layout.py` enforces the rule by parsing the imports of every module under `src/`.

The move is already under way in the working tree: `junit.py`, `safezip.py`, `limits.py` and `trust.py` are in
`src/shared/`. `trust.py` holds the GitHub rule and imports `GhWorkflowRun`, so it moves on to
`flakehunter_ingest_github/` to keep `shared` free of GitHub code.

Moving `_api` touches the tooling that names its path: `OUT` in `scripts/generate_client.py`, the staleness check in
`.github/workflows/ci.yml`, `extend-exclude` in `pyproject.toml` and the conventions in `CLAUDE.md`. The generated code
uses relative imports, so it is regenerated in place without changes. `pyproject.toml` lists all three packages under
`[tool.hatch.build.targets.wheel]`, and `src/shared/` gets an `__init__.py`; without both, the dev container's
`pip install -e .` would not install `shared` and the DAGs would fail to import it.

Each DAG is one file directly in `dags/`, named for its CI system. The file names differ from the package names, so
nothing in `dags/`, which Airflow puts on `sys.path`, can shadow a package in `src/`. All logic stays in the packages;
a DAG file only wires tasks together.

The GitHub DAG's id changes from `flakehunter_ingest` to `flakehunter_ingest_github`. Airflow keys run history by DAG
id, so the renamed DAG starts with an empty history and the old one is listed until it is deleted in the UI. With
`catchup` on, the new DAG re-runs its window on the first start; that is safe, since uploads are idempotent, and the
re-run uploads come back as `200` duplicates. Pause `flakehunter_ingest` before deploying the rename so the two do not
run side by side.

The name `shared` is generic: anything else on Airflow's `sys.path` called `shared` (a folder in `dags/` or `plugins/`,
another installed distribution) would shadow it or be shadowed by it. Nothing in this deployment uses the name today;
the layout test also rejects a `dags/shared` or `plugins/shared`.

## Code changes

Three commits, in this order. The first two change no behaviour.

1. **Restructure** (no GitLab code): finish the move above. Rename `flakehunter_ingest` to
   `flakehunter_ingest_github`, move `_api` and `client.py` into `shared` with the tooling changes listed above, move
   `trust.py` back to the GitHub package, move `download_artifact` from `github.py` to `shared/download.py`, and
   rename `dags/flakehunter_dag.py` to `dags/flakehunter_github_dag.py` with the new DAG id. Split
   `processrun.py`: the "zip bytes → XML files → merge → upload" step becomes `shared/upload.py`, taking a `CiRun` and
   a list of zip bytes, and the GitHub path calls it with no change in behaviour. Add `shared/run.py` with `CiRun` (run id,
   attempt, sha, branch, workflow, started at) and a `headers()` method that builds `RunHeaders`; the CI source joins
   it in step 2, and the upload connection stays in the DAG. Tests move to `tests/github/` and `tests/shared/`,
   import from the new paths and otherwise pass unchanged; the download tests move with `download_artifact`.
2. **Re-pin** to the FlakeHunter tag that adds `gitlab_ci` (see [FlakeHunter dependencies](#flakehunter-dependencies)):
   `contract/` and `src/shared/_api/` regenerated by the scripts, never edited by hand. The generated `X-FH-CI-Source`
   enum gains `gitlab_ci`. `RunHeaders` in `shared/client.py` gains an optional `ci_source`, passed to
   `post_api_v2_reports` as `x_fh_ci_source` when set and left `UNSET` otherwise; its docstring says the values come
   from the CI run, not specifically the GitHub `workflow_run`. The GitHub path keeps it unset, as today: FlakeHunter
   then records `github_actions`, so its uploads stay duplicates of the webhook's.
3. **GitLab**: the `flakehunter_ingest_gitlab` package above, `dags/flakehunter_gitlab_dag.py`, and
   `scripts/get_gitlab_fixture.py`, which records pipeline, job and artifact fixtures from a real project, like the
   GitHub scripts. GitLab tests go in `tests/gitlab/`. `CiRun` gains the CI source in step 2, sent by
   `headers()` only when set.

`junit.py`, `safezip.py` and `limits.py` move but do not change.

## Validation

- **Unit tests** (`respx`, recorded fixtures): header mapping from a pipeline payload, including
  `X-FH-CI-Source: gitlab_ci`; attempt derivation with no retries, one retry and retries across several jobs; skipping
  non-terminal pipelines and non-SHA-1 commits; a null `started_at`; trust for each source and for same-project and
  fork merge requests; merging XML from several jobs; size limits.
- **Contract:** `tests/test_contract.py` follows the re-pin: `test_pinned_version` takes the new `info.version`,
  `test_run_headers_cover_the_documented_set` includes `ci_source`, and `test_sent_headers_are_declared_and_valid`
  also runs with GitLab headers, so `gitlab_ci` is checked against the pinned enum.
- **Layout:** `tests/test_layout.py` fails if `shared` imports a CI package, one CI package imports the other, or a
  `dags/shared` or `plugins/shared` exists.
- **Regression:** after the restructure commit, the existing GitHub tests pass with only their imports changed,
  including `test_ci_source_is_left_to_the_github_default`: GitHub uploads still send no `X-FH-CI-Source`.
  `generate_client.py` followed by `git diff --exit-code -- src/shared/_api` shows no change, and
  `airflow dags list-import-errors` in the dev container is empty and `airflow dags list` shows
  `flakehunter_ingest_github`.
- **End to end:** in the dev container, `airflow dags test flakehunter_ingest_gitlab` against a local FlakeHunter
  at the re-pinned tag, with a `gitlab` repository registered, and a gitlab.com test project. Run the interval twice
  and expect `201`s then `200` duplicates, each response with `run.ciSource: "gitlab_ci"` and `run.ciRunId` equal to
  the pipeline id. Retry one job, run again and expect one new `201` with `run.attempt: 2` on the same SHA. The run
  appears in `GET /api/v2/tests/{id}/history`, and `GET /api/v2/repos` lists the project with `host: "gitlab"`.

## Implementation notes

- **Attempt:** one `include_retried=true` job listing gives both numbers. Job names are unique in a pipeline and a
  retry adds a job of the same name, so the current jobs are the highest id per name and the attempt is
  `1 + all jobs − current jobs`. This needs no `retried` flag in the job payload.
- **Pipeline running again:** `upload_pipeline` re-reads the pipeline. If it is no longer terminal, or a current job
  is not in a finished state (`success`, `failed`, `canceled`, `skipped`, `manual`), it uploads nothing and the
  pipeline is picked up by a later run with the new attempt.
- **Per-job archives:** a job archive over 10 MiB (listed or streamed), rejected, or failing to download is left
  out and logged; the other jobs' XML is still uploaded. A pipeline with no archives uploads nothing.
- **No XML, no upload:** when the downloaded archives hold no `.xml` file, `shared/upload.py` uploads nothing
  and logs it, for both DAGs. Before, an empty `<testsuites>` was uploaded and used up the run's upload key, so
  the run could not be uploaded again once its CI config was fixed. Seen on the test project
  (`g26work-group/flakehunter-test-gitlab`, project id `87833569`): its test job had JUnit only under
  `reports:junit`, and the pipeline's one archive held `node_modules`.
- **Merge request refs:** only `refs/merge-requests/<iid>/head` yields an iid. Merged-results pipelines
  (`…/merge`) therefore fail the trust check and are skipped, which answers open question 2 conservatively for now.
  A 404 for the merge request also counts as untrusted.
- **Branch:** `X-FH-Branch` is `pipeline.ref` as planned, so merge request pipelines record
  `refs/merge-requests/<iid>/head`, not the source branch.
- **Lookback:** `updated_after` is now minus 7 days (`LOOKBACK` in the DAG file). It only bounds discovery and is
  never sent. Like the GitHub DAG, the DAG has `schedule=None` and sets no pool.
- **Auth:** the GitLab token is sent as `Authorization: Bearer`, not `PRIVATE-TOKEN`, so httpx drops it if an
  artifact download redirects to another host.
- **Fixtures:** the unit tests use small hand-written payloads. `scripts/get_gitlab_fixture.py` records real ones.

## Open questions

1. ~~Can JUnit files declared only under `artifacts:reports:junit` be downloaded through the jobs API?~~
   Answered: no. A reports-only job lists a `junit` artifact but no `archive`, and the jobs API downloads only the
   archive. JUnit files must also be under `artifacts:paths`, with `when: always` so failing jobs keep them.
2. Merged-results pipelines test a merge commit, so `pipeline.sha` is not a commit on the branch. Should those
   pipelines be uploaded, skipped, or tagged by branch?
3. Child pipelines (`parent_pipeline` source) often hold the test jobs in monorepos. Are they needed in the first
   version? Including them means walking bridge jobs and deciding which pipeline id the report belongs to.
4. What run time does FlakeHunter record when `X-FH-Timestamp` is omitted? If it is the upload time, pipelines
   without `started_at` could fall back to `pipeline.created_at` instead.

## Not in scope

- Results of retried jobs as separate attempts.
- More than one GitLab host per deployment.
- A GitLab webhook or a `gitlab_ci` adapter in FlakeHunter; uploads from this DAG are the only GitLab path.
- FlakeHunter changes, which are planned in that repo.
