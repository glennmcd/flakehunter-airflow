# Security brief: artifact download and extraction

Hardens the path from GitHub artifact to merged JUnit XML. It covers findings 1, 3, 4, 8 and 9 of the security
review of 2026-10-17. The artifact zip is written by whoever pushes to a configured repository, so every step treats
it as untrusted, as FlakeHunter's webhook does (`apps/api/src/ingest/zipExtract.ts`, `limits.ts`).

## Findings

| # | Severity | Where | Problem |
|---|---|---|---|
| 1 | Medium | `github.py:23-40` `download_artifact` | Reads the whole response with `response.content`. `GhArtifactSpec.size_in_bytes` is never checked. A multi-GB artifact exhausts worker memory or disk on every DAG run. |
| 3 | Medium | `limits.py:2`, `safezip.py`, `junit.py:20-29` | Total cap is 100 MB, about 9x FlakeHunter's 11 MiB. Every entry is extracted to disk, not only `.xml`. The ratio and size checks use sizes the zip declares. ElementTree then parses up to 100 MB. |
| 4 | Low | `safezip.py:46` | `startswith(abspath(target_dir))` has no trailing separator, so `../extracted_evil/x.xml` passes and is written outside the target directory. |
| 8 | Low | `github.py:28` | `mkdtemp` scratch directories (zip, extracted files, `suites.xml`) are never deleted. |
| 9 | Low | `github.py:43-77` | Leftover `download_first_unexpired_artifact` sends `Bearer None` when `GITHUB_TOKEN` is unset, writes to a predictable path in `/tmp`, and has no size cap. |

## Approach

The limits keep the data small: at most a 10 MiB zip holding at most 11 MiB of XML. So the zip and its XML stay in
memory and never touch disk. Findings 4 and 8 then disappear instead of being patched: nothing is extracted, so there
is no zip-slip, and nothing is written, so there is nothing to clean up.

```text
spec = first non-expired artifact
  → size check (listed)
  → zip_bytes = download_artifact()      streamed, capped
  → files = read_xml_entries(zip_bytes)  .xml only, capped on actual bytes
  → xml = merge_junit(files)
  → upload_report()
```

## Steps

### 1. One set of limits (`limits.py`)

Match FlakeHunter's `apps/api/src/ingest/limits.ts`:

```python
MAX_ARTIFACT_ZIP_BYTES = 10 * 1024 * 1024  # compressed: listed size and downloaded size
MAX_REPORT_BYTES = 11 * 1024 * 1024  # 11,534,336: all XML in one artifact, decompressed
MAX_ZIP_ENTRIES = 1000  # files and directories


class ArtifactRejected(ValueError):
    """The artifact is refused for its size or shape. The message is fixed text, safe to log."""
```

- Remove `MAX_TOTAL_SIZE` and `MAX_RATIO`.
- `client.MAX_UNCOMPRESSED_BYTES` imports `MAX_REPORT_BYTES` instead of defining its own number.

### 2. Capped download (`github.py`, finding 1)

`download_artifact(client: httpx.Client, url: str) -> bytes`

- Stream with `client.stream("GET", url)` and `iter_bytes()`.
- If `Content-Length` is present and over `MAX_ARTIFACT_ZIP_BYTES`, raise `ArtifactRejected` before reading the body.
- Keep a running total and raise `ArtifactRejected` as soon as it passes `MAX_ARTIFACT_ZIP_BYTES`.
- Return the bytes. Write no file.
- Do not put the URL in exception text or logs after a redirect: it can be a signed blob URL.

In `processrun.py`, check `spec.size_in_bytes > MAX_ARTIFACT_ZIP_BYTES` **before** downloading, as
`processWorkflowRun.ts:74` does.

### 3. In-memory XML reader (`safezip.py`, findings 3 and 4)

Replace `safe_zip_check_extract` and `safe_stream_extract` with:

`read_xml_entries(zip_bytes: bytes) -> dict[str, bytes]`

- Open `zipfile.ZipFile(io.BytesIO(zip_bytes))`.
- Raise `ArtifactRejected` if `len(archive.infolist()) > MAX_ZIP_ENTRIES`.
- Skip directories and every entry whose name does not end in `.xml` (case-insensitive), without reading it.
- Read each `.xml` entry with `archive.open(info)` in 64 KB chunks. Keep one running total of **actual** bytes across
  all entries and raise `ArtifactRejected` as soon as it passes `MAX_REPORT_BYTES`. Never trust `file_size` or
  `compress_size`.
- Return `{entry_name: xml_bytes}`. Entry names are labels for logs only and are never used as paths.

### 4. Merge from bytes (`junit.py`)

`merge_junit(files: dict[str, bytes]) -> bytes`

- Parse each file with `ET.fromstring` and return the merged `<testsuites>` document as bytes, with one XML
  declaration.
- Replaces `get_combined_artifact(paths, output_path)`.
- Delete `extract_testsuite`: it reads every `.xml` in a zip with no limits.
- See open question 1 for how roots are handled.

### 5. Wire it up (`processrun.py`)

- Follow the flow in [Approach](#approach).
- Remove `construct_suites` and `extract_artifact`.
- Catch `ArtifactRejected`, log its fixed message with the run id, and return, as the function does today when no
  artifact is found.

### 6. Delete the leftover downloader (`github.py`, finding 9)

Delete `download_first_unexpired_artifact` and its test `test_github_download_zip` (`tests/test_github.py:43`).

## Tests

All offline: zips are built in memory with `zipfile`, HTTP is mocked with `respx`.

| Case | Expect |
|---|---|
| Listed `size_in_bytes` = 10 MiB + 1 | rejected; the download route is never called |
| Download streams 10 MiB + 1 bytes, no `Content-Length` | `ArtifactRejected`; reading stops early |
| `Content-Length` over the limit | rejected before the body is read |
| Zip with 1001 entries | rejected |
| Zip bomb: one `.xml` that inflates past 11 MiB from a small compressed size | rejected; reading stops at the cap |
| Two `.xml` entries, each under the cap, together over it | rejected (the cap is cumulative) |
| Large `.txt` and `.zip` entries next to a small `.xml` | only the `.xml` is returned; the others are never read |
| Entry named `../../evil.xml` | returned as a label only; nothing is written to disk |
| Fixture-repo artifact: `flaky.xml`, `unit/math.xml`, `legacy-testsuite.xml`, `notes.txt` | three XML files merged; `notes.txt` skipped |

Rewrite `tests/test_safezip.py` for `read_xml_entries` (its tests monkeypatch the removed `MAX_RATIO` and
`MAX_TOTAL_SIZE`), and move `tests/test_junit.py` to `merge_junit`.

## Not in scope

- DAG wiring: the `expand` XCom fix and `upload_run` returning the upload outcome.
- Moving credentials from Variables to Connections.
- Finding 2 (fixture scripts print the GitHub token) and findings 5, 6 and 7 (trust filter with null ids, header
  values, repo validation).
- `client.py` beyond the shared constant, and the generated `_api/`.

## Risks

- **Memory.** Peak is about the 10 MiB zip, 11 MiB of XML and its ElementTree: tens of MB, far below today's 100 MB
  ceiling.
- **Rejections are not visible in `summarize` yet.** A refused artifact is logged and the task succeeds. It shows in
  the summary only once `upload_run` returns the outcome.
- **A failed download still returns quietly** instead of raising for an Airflow retry. Unchanged here; follow-up.

## Validation

- `ruff check .` and `pytest`, offline.
- `airflow dags test flakehunter_ingest` in the dev container against a new fixture-repo run with the four-file
  artifact.

## Open questions

1. **Bare `<testsuite>` roots are merged wrongly.** `junit.py:28-29` appends each child of a file's root to the
   combined `<testsuites>`. For a file whose root is `<testsuite>` (the fixture's `legacy-testsuite.xml`), that puts
   the `<testcase>` elements directly under `<testsuites>` and drops the suite. FlakeHunter's parser reads cases only
   inside a `<testsuite>`, so those results are lost without an error. Proposed rule for `merge_junit`: nest a
   `<testsuite>` root whole; lift the child suites only from a `<testsuites>` root. One extra test. Fix it in step 4,
   or separately?
