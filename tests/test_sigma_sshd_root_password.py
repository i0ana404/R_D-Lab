"""rules/sshd_root_password_login.yml fires on its positive sample and stays quiet on its negative one (R-03, R-07).

The ECS samples hold, one JSON object per line, the events that
logstash/pipeline/20-filter-sshd.conf produces for the raw lines in
tests/samples/sshd_root_password_{positive,negative}.log.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from sigma_match import rule_matches

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = Path(__file__).resolve().parent / "samples"
RULE = ROOT / "rules" / "sshd_root_password_login.yml"
COMMITTED_QUERY = ROOT / "rules" / "opensearch" / "sshd_root_password_login.json"


def load_events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


POSITIVE = load_events(SAMPLES / "ecs_sshd_root_password_positive.json")
NEGATIVE = load_events(SAMPLES / "ecs_sshd_root_password_negative.json")


def event_id(event):
    return f"{event['user']['name']}@{event['source']['ip']}"


@pytest.mark.parametrize("event", POSITIVE, ids=event_id)
def test_rule_fires_on_positive_event(event):
    assert rule_matches(RULE, event), f"rule did not fire on: {event['event']['original']}"


@pytest.mark.parametrize("event", NEGATIVE, ids=event_id)
def test_rule_stays_quiet_on_negative_event(event):
    assert not rule_matches(RULE, event), f"rule fired on: {event['event']['original']}"


def test_committed_opensearch_query_matches_fresh_conversion():
    sigma = shutil.which("sigma")
    if sigma is None:
        pytest.skip("sigma is not on PATH")
    result = subprocess.run(
        [sigma, "convert", "-t", "opensearch_lucene", "--without-pipeline", "-f", "dsl_lucene", str(RULE)],
        capture_output=True, text=True, timeout=120, cwd=ROOT,
    )
    assert result.returncode == 0, f"sigma convert failed:\n{result.stderr[-4000:]}"
    fresh = json.loads(result.stdout)
    committed = json.loads(COMMITTED_QUERY.read_text(encoding="utf-8"))
    assert fresh == committed, (
        f"{COMMITTED_QUERY.relative_to(ROOT)} is stale; regenerate it from {RULE.relative_to(ROOT)}"
    )
