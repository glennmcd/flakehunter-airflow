# Security policy

## Reporting a vulnerability

Report vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/glennmcd/flakehunter-airflow/security/advisories/new).
Do not open a public issue, pull request or discussion for a security problem.

Include what you found, how to reproduce it and the commit or version affected. You should get a reply within
a week.

## Scope

In scope:

- The DAGs in `dags/` and the code in `src/`, for example handling of untrusted GitHub
  artifacts (zip and JUnit XML parsing), token handling and upload headers.
- The GitHub Actions workflows in `.github/workflows/`.

Out of scope:

- FlakeHunter itself. Report those issues to
  [glennmcd/flakehunter](https://github.com/glennmcd/flakehunter/security).
- Apache Airflow and other third-party dependencies. Report those upstream.

## Supported versions

Only the latest commit on `main` is supported.
