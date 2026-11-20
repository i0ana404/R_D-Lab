# Evidence

Screenshots and exports that back the Evidence column of [RISK-REGISTER.md](../../RISK-REGISTER.md).
Each file is listed once, under the risk it mainly supports; the Risks column names every risk it covers.

Before publishing, every screenshot was checked for the owner's public IP, `user@host` prompts, local Windows paths, keys and tokens; those are cropped or covered.
Screenshots marked *re-taken 2026-11-19/20* were captured again from the closed pull request, the ruleset page or the VM because the original was not saved; they show the same state.

## R-01: protected main branch and automated review

| File | Shows | Risks |
|---|---|---|
| r01-push-rejected.png | A direct `git push` to main rejected by the ruleset | R-01 |
| r01-protected-branch.png | A web edit on main is refused: GitHub offers only a new branch and a pull request | R-01 |
| r01-ruleset-required-checks.png | Required status checks gitleaks, lint, test, scan | R-01 |
| r01-pr-required-checks.png | Lab 4 pull request: lint, scan, test, gitleaks green and Required | R-01 |
| r01-ci-first-run-green.png | First green CI run: lint, scan, test, gitleaks | R-01, R-03 |
| r01-claude-oauth-secret.png | `CLAUDE_CODE_OAUTH_TOKEN` stored only as a repository secret (value hidden) | R-01, R-15 |
| r01-claude-review-checks.png | The claude-review check running on a pull request | R-01, R-15 |
| r01-claude-review-comment.png | An inline finding from the automated reviewer on its own PR (skip fork PRs), later applied | R-01, R-12 |
| r01-ruleset-claude-review-required.png | Ruleset with the reviewer added as a required check (then named `review`, Lab 7) | R-01 |
| r01-claude-review-sloppy-pr-1.png | Demo PR #22: reviewer findings, part 1 | R-01, R-02, R-04 |
| r01-claude-review-sloppy-pr-2.png | Demo PR #22: reviewer findings, part 2 | R-01, R-02, R-04 |
| r01-claude-review-sloppy-pr-3.png | Demo PR #22: reviewer summary | R-01, R-04 |
| r01-sloppy-pr-merge-blocked.png | Demo PR #22 cannot be merged (lint failed) | R-01 |
| r01-ruleset-claude-review-renamed.png | Ruleset after the job rename: five required checks incl. claude-review (re-taken 2026-11-19) | R-01 |
| r01-pr-claude-review-renamed-required.png | PR #24: `claude-review / claude-review` marked Required | R-01 |
| [../ruleset-main.json](../ruleset-main.json) | Export of the ruleset (exported 2026-11-19, after the job rename) | R-01 |

## R-02: secrets

| File | Shows | Risks |
|---|---|---|
| r02-gitleaks-blocked.png | pre-commit gitleaks blocks a commit with a fake secret | R-02 |
| r02-push-protection.png | Repository settings: Secret Protection and push protection enabled | R-02 |
| r02-git-show-ciphertext.png | The committed secrets file holds only SOPS ciphertext | R-02 |
| r02-git-log-enc-only.png | Git history contains only encrypted secrets files | R-02 |
| r02-check-ignore.png | `.env.secrets` and private keys are git-ignored | R-02 |
| r02-env-secrets-perms.png | `.env.secrets` is mode 600 | R-02 |
| r02-make-secrets-both-files.png | `make secrets` decrypts both files into `.env.secrets`; only variable names shown | R-02 |
| r02-make-down.png | `make down` stops the stack | R-02 |
| r02-env-secrets-deleted.png | `.env.secrets` is gone after `make down` | R-02 |
| r02-docker-ps.png | Every published port bound to 127.0.0.1 | R-02 |
| r02-compose-check.png | compose.yaml: images pinned by version and digest, every port on 127.0.0.1 from `.env` | R-02, R-13 |
| r02-health-1.png | OpenSearch cluster health right after start (yellow: one replica unassigned on a single node) | R-02, R-09 |
| r02-health-3.png | Cluster health green, queried with the admin password typed at a prompt, not on the command line | R-02, R-09 |
| r02-cert-inspect.png | Front-door certificate (frontdoor.lab, localhost) issued by the internal step-ca intermediate, 24-hour validity | R-02 |
| r02-openssl-chain.png | `openssl` verifies the certificate chain | R-02 |
| r02-firefox-secure.png | Browser shows the front door as secure | R-02 |
| r02-firefox-chain.png | Browser certificate viewer: frontdoor.lab → Lab Root Intermediate CA → Lab Root Root CA | R-02 |
| r02-monitor-user-least-privilege.png | Monitor user check: health 200, search 403, write 403 | R-02, R-09 |
| claude-env-test-1.png | Claude Code refuses to read `.env` and explains why | R-02 |
| claude-env-test-2.png | Authorised guardrail test: the agent proves the hook with harmless canaries instead of the real `.env` | R-02 |
| guard-test-1.png | Guard hook unit test: reading a `.env` path is blocked (exit 2) | R-02 |
| guard-test-2.png | Guard hook unit test: reading a normal file is allowed (exit 0) | R-02 |
| guard-test-3.png | Guard hook unit test: `git push origin main` is blocked (exit 2) | R-01 |
| settings-powershell-docker-ask.png | Claude Code settings: Docker commands require approval | R-02 |
| ai-claim-env-example-missing.png | AI claimed `.env.example` was missing | R-02 (AI workflow) |
| ai-claim-env-example-check.png | The claim checked and found false | R-02 (AI workflow) |

## R-03: tested detection rules

| File | Shows | Risks |
|---|---|---|
| r03-make-test-pipeline-green.png | First pipeline tests in the VM: 10 passed | R-03 |
| r03-tuning-before-fail.png | Tuning test fails before the exclusion is added | R-03, R-06 |
| r03-tuning-after-green.png | Tuning test green after the exclusion | R-03, R-06 |
| r03-stale-query-detected.png | A stale committed OpenSearch query fails the test | R-03 |
| r03-make-test-all-green.png, r03-make-test-all-green-final.png, r03-make-test-28-green.png | Full test suite in the VM during Lab 5: 20, 27 and 28 passed, 0 failed | R-03 |
| r03-pr-lab5-checks-green.png | Lab 5 pull request checks green | R-03 |
| r03-index-pattern-fields.png | ECS fields in the OpenSearch index pattern | R-03 |
| r03-discover-all-events.png | All parsed sshd events in Discover | R-03, R-05 |
| r03-discover-rule-hits.png | Rule query hits: three different invalid users | R-03, R-06 |
| r03-data-ignored.png | `data/` (synthetic logs) is git-ignored (re-taken 2026-11-20) | R-03 |
| ai-review-codec-line.png | AI proposed `codec => "line"` (would never emit) | R-03 (AI workflow) |
| ai-review-codec-plain.png | Corrected to `codec => "plain"` | R-03 (AI workflow) |
| ai-claude-md-path-conflict.png | Claude Code stops on a path conflict with CLAUDE.md | R-03 (AI workflow) |
| ai-attack-tag-outdated.png | AI used an outdated ATT&CK tag, caught by `sigma check` | R-03 (AI workflow) |
| ai-no-rules-summary.png | Session 2, no project rules: the agent turned the OpenSearch security plugin off and committed straight to a branch it created | R-02, R-03 (AI workflow) |
| round3-summary.png | Session 2, with project rules: security plugin kept on, ports on 127.0.0.1, no password in files, and the agent lists what it could not verify | R-02, R-03 (AI workflow) |
| skill-check-guardrails.png, skill-check-guardrails-staged.png | The check-guardrails skill run on the repo and on staged changes | R-01, R-02 |
| memory-file-1.png | The memory index (MEMORY.md) | AI workflow |
| memory-file-2.png | The memory file for the port rule (session ID covered) | AI workflow |
| memory-recalled-1.png, memory-recalled-2.png | In a new session the agent applies the remembered port rule (`${VAR:-default}` on 127.0.0.1) unprompted | AI workflow |
| MEMORY.md, ports-from-env-vars.md | The project memory files themselves (session IDs removed) | AI workflow |
| ai-no-rules.md | Session 2: full agent output without project rules | R-03 (AI workflow) |
| ai-with-rules.md | Session 2: full agent output with project rules | R-03 (AI workflow) |

## R-07: root password login

| File | Shows | Risks |
|---|---|---|
| r07-root-rule-check-and-tests.png | `sigma check` and tests for the root password login rule | R-07 |

## R-08 and R-10: MISP enrichment and indicator quality

| File | Shows | Risks |
|---|---|---|
| r08-misp-running-localhost.png | MISP containers bound to localhost | R-08, R-02 |
| r08-misp-image-digests.png | MISP images and their digests recorded on the deploy host | R-08, R-13 |
| r08-misp-logged-in.png | Logged in to the MISP web UI on localhost (before the first feed fetch, no events yet) | R-08 |
| r08-misp-feed-enabled.png | CIRCL OSINT feed enabled | R-08 |
| r08-misp-events-fetched.png | Fetching the feed events | R-08 |
| r08-misp-pull-tests.png | `misp_pull` unit tests added and passing without a MISP server | R-08 |
| r08-misp-pull-ioc-count.png | Export result: unique IPs written to the lookup file | R-08, R-10 |
| r08-make-up-guard.png | `make up` refuses to start without the lookup file | R-08 |
| r08-make-test-all-passed.png | Full test suite green (Lab 6) | R-08 |
| r08-discover-threat-match.png | Event from a MISP-listed IP tagged `threat_match`, risk score 80, `misp:1621` (the real indicator IP is covered) | R-08 |
| r08-discover-clean.png | Event from a documentation IP (198.51.100.77): no tag, no risk score | R-08 |
| r04-pr-lab6-checks-green.png | PR #20 checks green (re-taken 2026-11-19) | R-08 |
| r10-warninglists-enabled.png | 135 of 159 warninglists enabled | R-10 |
| r10-feed-age-distribution.png | Indicator age distribution; 180-day age-out | R-10 |

## R-09: pipeline monitoring

| File | Shows | Risks |
|---|---|---|
| r09-make-test-all-passed.png | Full test suite green incl. promtool tests (Lab 7) | R-09 |
| r09-grafana-pipeline-healthy.png | Grafana dashboard, pipeline healthy | R-09 |
| r09-alert-firing-grafana.png | LogstashDown firing after Logstash was stopped | R-09 |
| r09-alert-resolved-grafana.png | Alert resolved after Logstash was started | R-09 |
| r04-pr-lab7-observability-checks-green.png | PR #23 checks green (re-taken 2026-11-19) | R-09 |

## R-11 and R-12: CI supply chain and fork safety

| File | Shows | Risks |
|---|---|---|
| r11-actions-pinning-required.png | Setting: actions must be pinned to a full SHA | R-11 |
| r11-demo-unpinned-blocked.png | Demo PR #16: an action pinned by tag; lint fails, scan skipped, merge blocked | R-11 |
| r11-demo-pinning-error.png | The pinning error message | R-11 |
| r11-dependabot-prs.png | Dependabot pull requests after the 7-day cooldown | R-11 |
| r12-workflow-permissions-readonly.png | Default workflow token read-only | R-12 |
| r12-fork-approval-all-external.png | Approval required for all external contributors | R-12 |

## R-13: container images

| File | Shows | Risks |
|---|---|---|
| r13-ci-trivy-clean.png | Trivy in CI: front door on Alpine 3.24.4, 0 findings | R-13 |
| r13-demo-scan-failed.png | Demo PR #15: the scan fails on a vulnerable base image and the merge is blocked | R-13 |
| r13-demo-trivy-findings.png | Demo PR #15: 67 findings in nginx 1.27 (Alpine 3.21.3, end of life) | R-13 |
| r13-trivy-nginx-comparison.png | Trivy on nginx 1.27 / 1.30.5 / 1.30.6 | R-13 |
| r13-scan-new-cves-week-later.png | The same pinned image a week later: 3 new HIGH findings, scan fails | R-13 |
| r13-tag-moved-new-digest.png | A tag moved to a new digest | R-13 |
| r13-trivy-logstash-8.9.0.png | Logstash 8.9.0 image findings (known residual) | R-13 |
| r13-dependabot-nginx-scan-failed.png | Dependabot PR #9: scan summary, 12 findings | R-11, R-13 |
| r13-dependabot-nginx-trivy.png | PR #9: the CVEs and their fixed versions (re-taken 2026-11-19) | R-13 |
| r13-dependabot-nginx-closed.png | PR #9 closed with scan failed (re-taken 2026-11-19) | R-11, R-13 |
| r13-dependabot-sigma-conflict.png | Dependabot PR #19: pysigma dependency conflict, closed | R-11, R-13 |
| r13-release-run-green.png | Release v0.4.0 run green | R-13 |
| r13-release-v0.4.0-notes.png | Release v0.4.0 notes with risk IDs | R-13, R-04 |
| r13-release-v0.4.0-assets.png | Release v0.4.0 SBOM asset | R-13 |
| r13-release-v0.4.1-green.png | Release v0.4.1 run green with updated actions | R-11, R-13 |
| r13-release-v0.4.1-notes-assets.png | Release v0.4.1 notes and SBOM asset | R-13, R-04 |
| r13-cosign-verify.png | `cosign verify` of v0.4.0 | R-13 |
| r13-cosign-identity.png | Signer identity of v0.4.0 | R-13 |
| r13-cosign-verify-v0.4.1.png | `cosign verify` of v0.4.1 with the tag identity | R-13 |
| r13-cosign-digest-v0.4.1.png | Signed digest of v0.4.1 | R-13 |
| r13-syft-sbom.png | Syft SBOM of v0.4.0: 71 packages (same count as Trivy in CI) | R-13 |

## R-14: own exposure

| File | Shows | Risks |
|---|---|---|
| r14-shodan-host-403.png | The Shodan host API refuses the free plan (403 Forbidden), so the project switched to InternetDB | R-14 |
| r14-internetdb-exposure.png | InternetDB snapshot of the authorised IP: not indexed, no ports, no vulnerabilities (the IP itself is never shown or stored) | R-14 |
