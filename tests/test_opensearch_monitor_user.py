"""Tests for scripts/opensearch-monitor-user.in-container.sh (RISK-REGISTER R-02).

The script runs against a fake curl that answers like OpenSearch, so no cluster is needed.
They check that a least-privilege violation fails the run, that the probe indexes are
cleaned up, and that no password ever reaches a command line. Need a POSIX sh.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "opensearch-monitor-user.in-container.sh"
ADMIN_PW = "AdminPw0123456789"
MONITOR_PW = "MonitorPw0123456789"

FAKE_CURL = r"""#!/bin/sh
# Fake curl: logs method, URL and user (never the password), answers like OpenSearch.
cfg= out= method=GET url= data=
while [ $# -gt 0 ]; do
    case "$1" in
    -K) cfg=$2; shift ;;
    -o) out=$2; shift ;;
    -w | -H) shift ;;
    -X) method=$2; shift ;;
    --data-binary) data=$2; shift ;;
    -sk) ;;
    *) url=$1 ;;
    esac
    shift
done
user=$(sed -n 's/^user = "\([^:]*\):.*/\1/p' "$cfg")
echo "$method $url $user" >>"$CALLS"
echo '{}' >"$out"
case "$url" in
*"${TRANSPORT_FAIL:-no-such-url}"*) printf 000; exit 7 ;;
esac
case "$user:$method:$url" in
admin:GET:*/_plugins/_security/health) printf 200 ;;
admin:PUT:*monitor-read-probe*) printf "${READ_PROBE_CODE:-201}" ;;
admin:*) printf 200 ;;
prometheus:GET:*/_cluster/health) printf 200 ;;
prometheus:GET:*/monitor-read-probe/_search) printf "${READ_CODE:-403}" ;;
prometheus:PUT:*) printf "${WRITE_CODE:-403}" ;;
*) printf 500 ;;
esac
"""

pytestmark = pytest.mark.skipif(os.name == "nt" or shutil.which("sh") is None, reason="needs a POSIX sh")


def run_script(tmp_path, monitor_pw=MONITOR_PW, **codes):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text(FAKE_CURL)
    curl.chmod(0o755)
    calls = tmp_path / "calls.txt"
    calls.write_text("")
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "CALLS": str(calls),
        "OPENSEARCH_INITIAL_ADMIN_PASSWORD": ADMIN_PW,
        "OPENSEARCH_MONITOR_PASSWORD": monitor_pw,
        **codes,
    }
    result = subprocess.run(["sh", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=60)
    return result, calls.read_text()


def test_least_privilege_user_passes_and_cleans_up(tmp_path):
    result, calls = run_script(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "index search 403, write 403" in result.stdout
    assert "PUT https://localhost:9200/_plugins/_security/api/roles/prometheus_monitor admin" in calls
    assert "DELETE https://localhost:9200/monitor-read-probe admin" in calls


def test_user_that_can_read_index_data_fails_the_run(tmp_path):
    result, calls = run_script(tmp_path, READ_CODE="200")
    assert result.returncode != 0
    assert "search=200 (want 403)" in result.stderr
    assert "DELETE https://localhost:9200/monitor-read-probe admin" in calls


def test_user_that_can_write_fails_and_the_probe_is_removed(tmp_path):
    result, calls = run_script(tmp_path, WRITE_CODE="201")
    assert result.returncode != 0
    assert "write=201 (want 403)" in result.stderr
    assert "DELETE https://localhost:9200/monitor-write-probe admin" in calls


def test_transport_error_is_reported_and_probes_are_removed(tmp_path):
    result, calls = run_script(tmp_path, TRANSPORT_FAIL="monitor-read-probe/_search")
    assert result.returncode != 0
    assert "search=000 (want 403)" in result.stderr
    assert "DELETE https://localhost:9200/monitor-read-probe admin" in calls
    assert "DELETE https://localhost:9200/monitor-write-probe admin" in calls


def test_read_probe_create_failure_stops_before_monitor_checks(tmp_path):
    result, calls = run_script(tmp_path, READ_PROBE_CODE="500")
    assert result.returncode != 0
    assert "read probe create returned 500" in result.stderr
    assert "GET https://localhost:9200/monitor-read-probe/_search prometheus" not in calls
    assert "PUT https://localhost:9200/monitor-write-probe/_doc/1 prometheus" not in calls
    assert "DELETE https://localhost:9200/monitor-read-probe admin" in calls
    assert "DELETE https://localhost:9200/monitor-write-probe admin" in calls


def test_non_alphanumeric_password_is_refused_before_any_request(tmp_path):
    result, calls = run_script(tmp_path, monitor_pw='bad"pw\\x')
    assert result.returncode != 0
    assert "must be alphanumeric" in result.stderr
    assert calls == ""


def test_passwords_never_reach_a_command_line(tmp_path):
    _, calls = run_script(tmp_path)
    assert ADMIN_PW not in calls and MONITOR_PW not in calls
