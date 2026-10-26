#!/usr/bin/env bash
# guard.sh - PreToolUse hook for Claude Code (R-01, R-02).
# Claude Code sends the pending action as JSON on stdin.
# exit 0 = allow (normal permission rules still apply)
# exit 2 = block; the message on stderr is shown to Claude.
# Fails closed: if the action cannot be checked, it is blocked.

payload="$(cat)"

# Find a working Python ("python" on Windows, "python3" on Linux/macOS).
PY=""
for candidate in python python3; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys" >/dev/null 2>&1; then
    PY="$candidate"; break
  fi
done
if [ -z "$PY" ]; then
  echo "guard.sh: Python not found, so the action cannot be checked. Blocked." >&2
  exit 2
fi

printf '%s' "$payload" | "$PY" -c '
import json, re, sys

def block(reason):
    print("Blocked by guard.sh: " + reason, file=sys.stderr)
    sys.exit(2)

try:
    data = json.loads(sys.stdin.read())
except Exception:
    block("the action could not be read, so it cannot be checked.")

tool = data.get("tool_name", "")
inp = data.get("tool_input") or {}

# 1. Files that hold secrets (R-02). .env.example is allowed: it holds no secrets.
SECRET = r"(^|/)(\.env(\.[\w.-]+)?|secrets/.*|.*\.(pem|key)|id_(rsa|ed25519|ecdsa)(\.pub)?|\.ssh/.*|.*sops/age/.*|keys\.txt)$"
EXAMPLE = r"(^|/)\.env\.example$"

def check_path(p):
    n = str(p).replace("\\", "/").lower()
    if n and not re.search(EXAMPLE, n) and re.search(SECRET, n):
        block("access to a secret file is not allowed: " + str(p) + " (R-02)")

if tool in ("Read", "Edit", "Write", "NotebookEdit"):
    check_path(inp.get("file_path") or inp.get("notebook_path") or "")
elif tool in ("Grep", "Glob"):
    check_path(inp.get("path") or "")
    check_path(inp.get("pattern") or "")

# 2. Shell commands (Bash and PowerShell).
if tool in ("Bash", "PowerShell"):
    c = str(inp.get("command", "")).replace("\\", "/").lower()
    RULES = [
        (r"(^|[\s\"\x27=/*(,])\.env(?!\.example)(\.[\w.-]+)?($|[\s\"\x27;|&)>,])", "commands may not touch .env files (R-02)."),
        (r"(^|[\s\"\x27=/])(secrets/|\.ssh/)|sops/age|\bkeys\.txt\b|\bid_(rsa|ed25519|ecdsa)\b", "commands may not touch secrets or keys (R-02)."),
        (r"--no-verify", "--no-verify would skip the gitleaks pre-commit check (R-02)."),
        (r"\bgit\b[^;&|]*\bpush\b[^;&|]*(\s--force|\s-f\b|\s\+)", "force push is not allowed (R-01)."),
        (r"\bgit\b[^;&|]*\bpush\b[^;&|]*\b(main|master)\b", "pushing to main is not allowed; open a pull request (R-01)."),
        (r"\bgh\s+pr\s+merge\b", "only the owner merges pull requests (R-01)."),
        (r"\bsops\b[^;&|]*\s(-d|--decrypt)\b", "decrypting secrets is done by a person at deploy time (R-02)."),
        (r"\b(curl|wget|irm|iwr|invoke-restmethod|invoke-webrequest)\b[^;&]*\|\s*(bash|sh|iex|invoke-expression)\b", "piping a download into a shell is not allowed."),
        (r"\bdocker\b[^;&|]*--privileged", "privileged containers are not allowed."),
        (r"\bprintenv\b|(^|[;&|]\s*)(env|set)\s*($|[;&|])", "dumping environment variables could expose secrets (R-02)."),
    ]
    for pattern, reason in RULES:
        if re.search(pattern, c):
            block(reason)
    for part in re.split(r"[;&|]+", c):
        if re.search(r"\bdocker\s+(container\s+)?run\b", part) and "--rm" not in part:
            block("docker run must include --rm so no container is left behind.")

sys.exit(0)
'
