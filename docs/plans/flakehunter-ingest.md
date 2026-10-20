# flakehunter_ingest

`flakehunter_ingest` is an Airflow 3 DAG that pulls JUnit XML artifacts from GitHub Actions runs and uploads them to
FlakeHunter through `POST /api/v2/reports`. It runs alongside the FlakeHunter webhook: it catches runs the webhook missed
and backfills repositories added later. Both paths write the same records, so running both never counts a run twice.

The contract is FlakeHunter's `docs/openapi.v2.json` (`info.version` 2.0.0). Idempotency follows
[ADR 0005](https://github.com/glennmcd/flakehunter/blob/main/docs/decisions/0005-upload-api-xml-and-headers.md):
uploading the same run, attempt and report key again is a no-op that returns `200` with the original counts.

## Shape

```text
discover_runs  ──►  upload_run.expand(run)  ──►  summarize
```

- **`discover_runs`** lists completed workflow runs for each configured repository, created in the data interval plus a
  24-hour lookback (`GET /repos/{owner}/{repo}/actions/runs?status=completed&created=>=…`). It drops runs that the
  webhook would also refuse (see [Trust](#trust)) and returns one small descriptor per run.
- **`upload_run`** is mapped once per run. It picks the run's artifact, extracts the XML files, merges them into one
  `<testsuites>` document, gzips it and uploads it.
- **`summarize`** counts stored, duplicate, skipped and rejected runs per repository. It fails the DAG run when any
  run was rejected, so rejections show up in the Airflow UI.

Schedule: hourly, `catchup=False`. A manual run with a wide data interval does a backfill. GitHub's artifact retention
(90 days by default) sets how far back a backfill can go.

## Idempotency

The upload key is (repository, `X-FH-Run-Id`, `X-FH-Run-Attempt`, `X-FH-Report-Key`). Every part comes from GitHub,
never from Airflow:

| Header | Source |
|---|---|
| `X-FH-Run-Id` | `workflow_run.id` |
| `X-FH-Run-Attempt` | `workflow_run.run_attempt` |
| `X-FH-Sha` | `workflow_run.head_sha` |
| `X-FH-Branch` | `workflow_run.head_branch` |
| `X-FH-Workflow` | `workflow_run.name` |
| `X-FH-Timestamp` | `workflow_run.run_started_at` |
| `X-FH-Report-Key` | `webhook-artifact`, always |

The DAG never uses `dag_run.run_id`, the logical date or the task try number in a header. With that rule, task
retries, cleared tasks, overlapping lookback windows and repeated backfills all produce the same requests, and
FlakeHunter answers every repeat with `200`. Discovery needs no cursor or watermark state.

**Matching the webhook.** The webhook stores one report per run under the key `webhook-artifact`. It reads the first
non-expired artifact and skips any run that already has a report. Report keys are unique per run, so an upload under
any other key would add a second copy of the results. The DAG therefore mirrors the webhook:

- one upload per run, with the key `webhook-artifact`;
- the first non-expired artifact in `GET /repos/{owner}/{repo}/actions/runs/{run_id}/artifacts`, in API order;
- every `.xml` file in the artifact zip, merged into one `<testsuites>` document.

If the webhook ingested the run first, the upload returns `200`. If the DAG got there first, the webhook finds a
report and does nothing.

One difference remains. The upload API has no file-name header, so suites ingested through the DAG have no
`file_name`, while webhook-ingested suites do. Flaky detection does not use the column.

## Responses

| Response | Outcome | Retry |
|---|---|---|
| `201` | stored | — |
| `200`, `duplicate: true` | duplicate, counted as success | — |
| `429` | wait `Retry-After` seconds, then send again, at most 3 times within the task | inside the task |
| `5xx`, timeout, connection error | raise; Airflow retries with exponential backoff (3 retries) | task retries |
| `400`, `401`, `413`, `422` | rejected, recorded with `error.code`, `error.message` and `requestId` | never |

Rejections do not raise inside `upload_run`, so one bad report does not stop the other mapped tasks. `summarize` fails
the run afterwards. A `400` can mean a header failed validation or that the SHA contradicts an existing run. Both
share the code `validation_error`, and both are treated as rejections.

## Limits

- **Size.** The DAG always gzips the body (`Content-Encoding: gzip`), because the AWS deployment caps request bodies
  near 6 MB. A merged document over 11,534,336 bytes uncompressed is rejected locally and never sent. The artifact zip
  is checked against FlakeHunter's 10 MiB artifact limit before download, as the webhook does.
- **Rate.** FlakeHunter allows 120 uploads a minute per token and per source IP. Every upload runs in the Airflow
  pool `flakehunter_upload` (4 slots), which keeps a backfill well under that limit.
- **GitHub API.** Discovery and artifact downloads use a GitHub token, with a limit of 5,000 requests an hour.
  Each run costs about three requests.

## Trust

Whoever writes a run's code controls its artifact. The DAG applies the same filter as FlakeHunter's
`workflowRunSkipReason`:

- the run's `event` is one of `push`, `pull_request`, `merge_group`, `schedule` or `workflow_dispatch`;
- `head_repository.id` equals the repository's id.

Runs that fail either check are counted as skipped and never uploaded.

## Configuration

| Item | Kind | Contents |
|---|---|---|
| `flakehunter_repos` | Variable (JSON) | list of `owner/repo` |
| `github_default` | Connection | GitHub token with read access to Actions (`actions:read`) on those repositories |
| `flakehunter_upload_<owner>_<repo>` | HTTP Connection | host = FlakeHunter base URL, password = that repository's upload token |

Upload tokens are per repository ([ADR 0006](https://github.com/glennmcd/flakehunter/blob/main/docs/decisions/0006-read-token-and-upload-tokens.md)),
and FlakeHunter takes the repository from the token. A Connection holding the wrong repository's token would write
results into that repository, and nothing on the upload path would notice. The connection name is the only safeguard,
so keep it in sync with the token's repository.

## Layout

```text
dags/flakehunter_ingest.py      DAG definition (airflow.sdk TaskFlow, dynamic task mapping)
src/flakehunter_ingest/
  github.py                     run listing, attempt fields, artifact download
  junit.py                      zip extraction and <testsuites> merge
  client.py                     httpx client for POST /api/v2/reports
  trust.py                      trigger and head-repository checks
contract/openapi.json           copy of FlakeHunter's contract, pinned at 2.0.0
tests/
```

The code is plain Python and testable without Airflow. The DAG file only wires the pieces together. The project uses
`uv`, `pytest` and `ruff`.

## Validation

- **Unit tests:** header mapping from a `workflow_run` payload; the JUnit merge (single `<testsuite>`, nested
  `<testsuites>`, XML declarations, a non-XML file in the zip); trust filtering; every row of the response table,
  with `respx` mocks.
- **Contract test:** the header names, types and patterns the client sends match `contract/openapi.json`. It fails
  when the copied spec changes in a way the client does not follow.
- **End to end:** on the Linux VM, `airflow dags test flakehunter_ingest` against a local FlakeHunter and a test
  repository. Run the same interval twice: the first run reports `201`s, the second only duplicates. Then let the
  webhook ingest a new run and check that the DAG reports it as a duplicate.

## Not in scope

- FlakeHunter's read endpoints, and any change to the FlakeHunter API.
- Attempts older than a run's latest. The runs listing returns the latest attempt only, and artifacts are listed per
  run rather than per attempt, so an earlier attempt's results cannot be recovered reliably.
- Installing and operating Airflow on the VM.
