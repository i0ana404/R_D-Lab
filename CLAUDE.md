# CLAUDE.md

Instructions for AI coding agents working in this repository.

## Project

SSH brute-force detection with threat-intelligence enrichment.
The system reads sshd logs, detects attack patterns with Sigma rules, checks source IPs against a MISP list of malicious IPs and raises alert severity on a match.

Out of scope: blocking IPs, exposing anything to the internet, using real logs. Use only synthetic logs.

Risks and controls are tracked in RISK-REGISTER.md. Every change must serve a risk ID from it.

## Security rules (never break these)

- Never disable authentication or TLS to avoid handling secrets. Secrets are encrypted with SOPS and age.
- Never write passwords, API keys or tokens into any file. Use placeholders and document them.
- Never read, print or search `.env` files, `secrets/`, SSH keys or age keys.
- Never decrypt secrets (`sops -d`). Decryption happens only at deploy time, run by a person.
- Never use `:latest` or untagged images. Pin every image by version and digest, and never choose a version without stating where it was verified.
- Bind every published port to `127.0.0.1`.
- Never use `--no-verify`, never force push, never push to `main`, never merge pull requests.
- Never run `git commit` or `git push` without the owner approving the exact command.
- Do only what was asked. Do not add files or settings that were not requested; propose them instead.

## Stack conventions

- OpenSearch, OpenSearch Dashboards and Logstash run with Docker Compose (`docker-compose.yml` in the repository root).
- Logstash pipelines go in `logstash/pipeline/`, named `NN-purpose.conf` (for example `20-filter-sshd.conf`).
- OpenSearch index templates go in `opensearch/templates/`.
- Sigma rules go in `rules/`, named `sshd_<technique>.yml`, each mapped to a MITRE ATT&CK ID.
- Log samples go in `tests/samples/`. Use only documentation IP ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32).
- Map log fields to Elastic Common Schema (ECS).
- `docker run` must always include `--rm`.

## Detection content

- Every Sigma rule ships with a positive sample (must match) and a negative sample (must not match).
- Every rule and pipeline has a pytest test in `tests/`. A rule without a passing test is not done.

## Workflow

- Work only on a branch named `<type>/<short-description>` (see CONTRIBUTING.md).
- Commit messages follow Conventional Commits: `<type>: <summary>`.
- Pull request descriptions start with `Addresses: R-xx`.
- When a control is implemented, update its row in RISK-REGISTER.md in the same pull request.
- If a rule here blocks the task, stop and explain; do not look for a workaround.
