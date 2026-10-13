# Security Policy

## Scope

This repository contains a lab project for SSH brute-force detection with threat-intelligence enrichment (ULBS Cybersecurity, Module 4). It uses only synthetic logs and is not exposed to the internet.

In scope: detection rules, pipeline and container configuration, CI workflows, scripts and documentation in this repository.
Out of scope: third-party components (OpenSearch, Logstash, MISP and others). Report those to their own maintainers.

## Supported versions

Only the current `main` branch is supported.

## Reporting a vulnerability

Do not open a public issue for security problems.
Report privately through the repository's **Security** tab, using **Report a vulnerability**.

Please include what you found, where (file, line or commit) and how to reproduce it.
Reports are acknowledged within 7 days.

## Secrets

No real credentials belong in this repository. If you find an API key, password or private key in any file or commit, report it as above so it can be revoked and removed from history. (Risk R-02)

## AI-assisted development

Parts of this repository are written with an AI coding agent. The same rules apply to the agent as to a human contributor:

- The agent never pushes to `main`; every change arrives through a pull request. (Risk R-01)
- Every pull request is reviewed by the code owner before merge. (Risk R-01)
- AI-generated detection rules must pass their positive and negative sample tests in CI. (Risk R-03)
- Commit messages follow Conventional Commits and pull requests cite the risk IDs they address. (Risk R-04)

A suspected security problem introduced by AI-generated content is reported the same way as any other vulnerability.

## Related documents

Risks and controls are tracked in [RISK-REGISTER.md](RISK-REGISTER.md).
