---
name: check-guardrails
description: Run the repository's guardrail checks (guard hook tests, settings.json validation, gitleaks on staged changes) and report the results. Use before opening a pull request and after any change to .claude/, .pre-commit-config.yaml or CLAUDE.md.
allowed-tools: Bash(bash tests/guard/test_guard.sh) Bash(python -m json.tool .claude/settings.json) Bash(python -m pre_commit run gitleaks) PowerShell(bash tests/guard/test_guard.sh) PowerShell(python -m json.tool .claude/settings.json) PowerShell(python -m pre_commit run gitleaks)
---

# Check guardrails

Run these three checks from the repository root with the Bash tool, or with the PowerShell tool when Bash is not available, in this order. Run each command exactly as written, with nothing added before or after it. Run every check even if an earlier one fails.

1. Guard hook tests (R-01, R-02):
   `bash tests/guard/test_guard.sh`
   Passes when the last line reads `0 failed`.

2. Claude Code settings are valid JSON (R-01, R-02):
   `python -m json.tool .claude/settings.json`
   Passes when the command exits without an error.

3. Secret scan on staged changes, the same check as the commit hook (R-02):
   `python -m pre_commit run gitleaks`
   Passes when the gitleaks line ends in `Passed` or `(no files to check)Skipped`.

## Report

Reply with one table: check, result (PASS or FAIL), and for a failure the exact failing lines from the output.

## Rules

- Do not change any file while running this skill, including to make a check pass.
- If a check fails, stop after the report and explain the likely cause. The owner decides the fix.
- Never use `--no-verify` and never skip a check.
- This skill checks the guardrails only. The full git history is scanned for secrets by the `secret-scan` workflow in CI.
