# Risk Register: SSH brute-force detection with threat-intelligence enrichment

## Scope

- **Problem:** an SSH bastion host is continuously targeted by bots guessing passwords. Without detection the attack is invisible.
- **What the project builds:** a system that reads sshd logs, recognises attack patterns with Sigma rules, checks the source IP against a MISP list of malicious IPs and raises alert severity on a match.
- **How it is built:** in Docker, in a protected Git repository, with an AI agent writing configuration under the owner's rules and automated checks (CI) before every merge.
- **Out of scope:** no IP blocking; nothing exposed to the internet; only synthetic logs created by the owner.

## Register

Register: Operational = risk from the AI agent in the engineering workflow · Internal = risk in the security function the project serves · External = risk from the live threat landscape.

| ID | Register | Asset | Threat / technique | ATT&CK ID | Vulnerability | L | I | Inherent | Control | Res. L | Res. I | Residual | Evidence | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | Operational | main branch of the detection repository | AI agent (Claude Code) pushes Sigma rules or Compose changes straight to main, bypassing review | n/a | Agent runs with the student's push rights; main has no ruleset | 4 | 4 | 16 (High) | GitHub ruleset on main: pull request required, required status checks, no direct or force push; CODEOWNERS on rules/ and .github/ | 1 | 4 | 4 (Low) |  |  | Open |
| R-02 | Operational | MISP and Shodan API keys | Agent or student commits a plaintext API key to the public repository | T1552.001 | Repository is public; no secret scanning before push | 4 | 5 | 20 (High) | pre-commit gitleaks hook plus gitleaks in CI; secrets encrypted with SOPS/age; .env listed in .gitignore | 2 | 3 | 6 (Low) |  |  | Open |
| R-03 | Operational | Sigma rules for sshd authentication logs | AI-generated rule uses a wrong field name or threshold and silently never fires | n/a | No tests; rule output accepted without validation | 4 | 4 | 16 (High) | Every rule ships with positive and negative sshd log samples; pytest and sigma-cli check run in CI; banned patterns listed in CLAUDE.md | 2 | 4 | 8 (Medium) |  |  | Open |
| R-04 | Operational | Audit trail (commit and pull request history) | Agent writes vague commit messages and pull requests that do not say which risk they address | n/a | No commit convention; no pull request template | 3 | 2 | 6 (Low) | Conventional Commits (docs:, feat:, fix:); pull request template requiring risk IDs; rule written in CLAUDE.md | 1 | 2 | 2 (Low) |  |  | Open |
| R-05 | External | SSH accounts on the bastion host | Bots run password guessing against sshd and the attack goes unnoticed | T1110.001 | Password authentication enabled; failed logins in the auth log are not monitored | 5 | 4 | 20 (High) | Sigma rule: N or more 'Failed password' events from one source IP within a time window raise an alert | 2 | 4 | 8 (Medium) |  |  | Open |
| R-06 | External | SSH accounts on the bastion host | Password spraying: one source IP tries a few passwords across many usernames and stays under per-user thresholds | T1110.003 | Thresholds count failures per user, not distinct users per source IP | 3 | 4 | 12 (Medium) | Sigma rule counting distinct usernames (including 'Invalid user') per source IP within a time window | 1 | 4 | 4 (Low) |  |  | Open |
| R-07 | External | Bastion host (initial access) | Successful login after a burst of failures from the same IP: the attack succeeded and looks like a normal login | T1078 | Successful logins are never correlated with earlier failures | 2 | 5 | 10 (Medium) | Correlation rule: 'Accepted' login after N or more failures from the same source IP is raised as critical. Fallback: if the OpenSearch Sigma backend cannot express this correlation, status becomes Accepted, with R-05 still alerting on the failure burst | 1 | 5 | 5 (Low) |  |  | Open |
| R-08 | External | Triage of brute-force alerts | Attacks from infrastructure already known as malicious get the same low severity as random scanner noise | T1110 | No threat-intelligence correlation on source IPs | 4 | 3 | 12 (Medium) | MISP feed exported with PyMISP to a lookup file; Logstash translate filter sets threat.indicator.matched and raises severity on a match | 2 | 3 | 6 (Low) |  |  | Open |
| R-09 | Internal | sshd log ingestion pipeline (Logstash to OpenSearch) | A log format change, malformed lines or a stopped container leave detections blind with no warning | n/a | No parser tests; no alert when logs stop arriving | 3 | 4 | 12 (Medium) | pytest on the Logstash pipeline with malformed and truncated samples, run in CI; Alertmanager rules for Logstash down and Logstash queue growing | 2 | 4 | 8 (Medium) |  |  | Open |
| R-10 | Internal | Severity decisions based on MISP indicators | Stale or false-positive indicators (for example reused cloud or shared IPs) escalate benign logins; analysts learn to ignore escalations | n/a | Indicators have no expiry; no allowlist of known-benign ranges | 3 | 3 | 9 (Medium) | Feed lifecycle: indicator expiry (age-out), deduplication and an allowlist of benign ranges, documented in docs/ | 2 | 2 | 4 (Low) |  |  | Open |

Evidence and Owner are filled in as each control is implemented. A row marked Implemented or Verified must have Evidence (template rule 4).

## Residual score justification

- **R-01** (16 → 4): Likelihood drops because the direct-push path is closed by the platform, not by discipline. Impact is unchanged: if review is bypassed anyway, the damage is the same.
- **R-02** (20 → 6): Two layers (local hook and CI) make a leak unlikely. Impact falls because keys are scoped to the lab and can be rotated.
- **R-03** (16 → 8): A broken rule fails the positive-sample test before merge. Impact is unchanged: a rule that slips through still leaves the attack unseen.
- **R-04** (6 → 2): The template forces a risk ID in every pull request, so the history reads as the register being closed row by row.
- **R-05** (20 → 8): The project detects, it does not block, so impact stays 4. What drops is the likelihood that the attack runs unseen.
- **R-06** (12 → 4): A dedicated rule closes the gap that R-05 leaves open by design.
- **R-07** (10 → 5): Impact stays 5 because a compromised account is still compromised; the rule makes it very unlikely that this happens unseen. If the fallback applies (status Accepted), the residual returns to the inherent 10 and is documented as a conscious gap.
- **R-08** (12 → 6): Known-bad sources are ranked first, so the analyst sees them first. This is the outcome Session 6 asks the enrichment to change.
- **R-09** (12 → 8): Parser regressions fail in CI before merge, and a stopped or stuck Logstash raises an alert. Residual likelihood stays 2 because a pipeline that runs but receives no sshd lines (for example a misconfigured log source) is not alerted; this gap is accepted for lab scope.
- **R-10** (9 → 4): Expiry removes most stale indicators; the remaining false positives affect a single alert, not trust in the whole system.

## Scales (from the course template)

| Score | Likelihood | Impact |
|---|---|---|
| 1 | Rare: no realistic path with current controls | Negligible: no effect on confidentiality, integrity or availability |
| 2 | Unlikely: requires unusual conditions or insider error | Minor: contained, fixed in hours, no data exposure |
| 3 | Possible: plausible within the project lifetime | Moderate: one component degraded, limited data exposure |
| 4 | Likely: expected without the control in place | Major: detections blind or secrets exposed, repo integrity at risk |
| 5 | Almost certain: already observed or trivially triggered | Severe: full compromise of the project or its credentials |

Score bands: 1–7 Low · 8–14 Medium · 15–25 High.

Status values: Open · Implemented (control exists) · Verified (evidence reviewed) · Accepted (risk consciously left as is, reason in Control).
