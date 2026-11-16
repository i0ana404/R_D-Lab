"""The sshd Logstash filter maps every sample line to ECS (R-03, R-05, R-06).

The tests run the real pipeline: logstash/pipeline/20-filter-sshd.conf between a
stdin input and a json_lines stdout output, inside the pinned Logstash image.
They are skipped if docker is not on PATH or no LOGSTASH_IMAGE is configured.
"""
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FILTER = ROOT / "logstash" / "pipeline" / "20-filter-sshd.conf"
HARNESS = Path(__file__).resolve().parent / "logstash"
SAMPLE = Path(__file__).resolve().parent / "samples" / "sshd_auth.log"

CONTAINER_PIPELINE = "/usr/share/logstash/pipeline"
TIMEOUT_SECONDS = 300


def _image_from_env_file(path):
    """Return LOGSTASH_IMAGE from a dotenv file. Reads only that one key and never prints the file."""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key.strip() == "LOGSTASH_IMAGE":
            value = value.strip().strip('"').strip("'")
            return value or None
    return None


def logstash_image():
    """LOGSTASH_IMAGE from the environment, else .env, else .env.example."""
    image = os.environ.get("LOGSTASH_IMAGE", "").strip()
    if image:
        return image
    return _image_from_env_file(ROOT / ".env") or _image_from_env_file(ROOT / ".env.example")


def run_pipeline(sample_path):
    """Feed sample_path through the real pipeline and return the output events as dicts."""
    if shutil.which("docker") is None:
        pytest.skip("docker is not on PATH; the Logstash pipeline tests need it")
    image = logstash_image()
    if not image:
        pytest.skip("no LOGSTASH_IMAGE in the environment, .env or .env.example")

    mounts = {
        HARNESS / "00-input-stdin.conf": "00-input-stdin.conf",
        FILTER: "20-filter-sshd.conf",
        HARNESS / "99-output-stdout.conf": "99-output-stdout.conf",
    }
    cmd = ["docker", "run", "--rm", "-i", "--network", "none",
           "-e", "LS_JAVA_OPTS=-Xms256m -Xmx256m"]
    for source, name in mounts.items():
        cmd += ["--mount", f"type=bind,source={source},target={CONTAINER_PIPELINE}/{name},readonly"]
    cmd += [
        image,
        # Only the NN-*.conf files, so the image's default logstash.conf is not loaded.
        "-f", f"{CONTAINER_PIPELINE}/[0-9][0-9]-*.conf",
        "--log.level", "error",
        "--pipeline.workers", "1",
    ]

    # Normalise line endings in case git checked the sample out with CRLF.
    data = Path(sample_path).read_bytes().replace(b"\r\n", b"\n")
    result = subprocess.run(cmd, input=data, capture_output=True, timeout=TIMEOUT_SECONDS)
    assert result.returncode == 0, (
        f"logstash exited with {result.returncode}:\n"
        f"{result.stderr.decode(errors='replace')[-4000:]}"
    )

    events = []
    for line in result.stdout.decode(errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and "message" in obj:
            events.append(obj)
    return events


def get(event, dotted):
    """event['a']['b'] for 'a.b', or None if any part is missing."""
    value = event
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


SAMPLE_LINES = [line for line in SAMPLE.read_text(encoding="utf-8").splitlines() if line.strip()]

# Expected ECS fields for each sshd form, keyed by sample line number (0-based).
# A value of None means the field must be absent.
SSHD_EXPECTED = {
    0: {  # Failed password for <user>
        "user.name": "root", "source.ip": "203.0.113.10", "source.port": 52211,
        "event.outcome": "failure", "system.auth.ssh.method": "password", "event.reason": None,
        "process.pid": 1234,
    },
    1: {  # Failed password for invalid user <user>
        "user.name": "admin", "source.ip": "203.0.113.11", "source.port": 52212,
        "event.outcome": "failure", "system.auth.ssh.method": "password", "event.reason": "invalid_user",
        "process.pid": 1235,
    },
    2: {  # Accepted password
        "user.name": "alice", "source.ip": "192.0.2.20", "source.port": 40022,
        "event.outcome": "success", "system.auth.ssh.method": "password", "event.reason": None,
        "process.pid": 1236,
    },
    3: {  # Accepted publickey ... ssh2: <key type> <fingerprint>
        "user.name": "bob", "source.ip": "198.51.100.30", "source.port": 40023,
        "event.outcome": "success", "system.auth.ssh.method": "publickey", "event.reason": None,
        "process.pid": 1237,
    },
    4: {  # Invalid user <user> from <ip> port <port>
        "user.name": "oracle", "source.ip": "203.0.113.12", "source.port": 52213,
        "event.outcome": "failure", "system.auth.ssh.method": None, "event.reason": "invalid_user",
        "process.pid": 1238,
    },
}
UNPARSED = {
    5: {"process.name": "CRON", "process.pid": 2001},   # another program
    6: {"process.name": "sshd", "process.pid": 1239},   # malformed sshd line (no port number)
}


def test_sample_covers_every_form():
    assert len(SAMPLE_LINES) == len(SSHD_EXPECTED) + len(UNPARSED)


@pytest.fixture(scope="module")
def events_by_line():
    events = run_pipeline(SAMPLE)
    by_original = {get(e, "event.original"): e for e in events}
    assert len(events) == len(SAMPLE_LINES), f"expected {len(SAMPLE_LINES)} events, got {len(events)}"
    missing = [line for line in SAMPLE_LINES if line not in by_original]
    assert not missing, f"no output event has event.original equal to: {missing}"
    return {i: by_original[line] for i, line in enumerate(SAMPLE_LINES)}


def _check_common(event, index):
    line = SAMPLE_LINES[index]
    assert get(event, "event.original") == line
    assert get(event, "host.hostname") == "lab-host"
    expected_ts = datetime.fromisoformat(line.split(" ", 1)[0])
    actual_ts = datetime.fromisoformat(event["@timestamp"].replace("Z", "+00:00"))
    assert actual_ts == expected_ts
    assert "_dateparsefailure" not in as_list(event.get("tags"))


@pytest.mark.parametrize("index", sorted(SSHD_EXPECTED))
def test_sshd_line_maps_to_ecs(events_by_line, index):
    event = events_by_line[index]
    _check_common(event, index)

    assert "_sshd_unparsed" not in as_list(event.get("tags"))
    assert get(event, "process.name") == "sshd"
    assert get(event, "event.kind") == "event"
    assert as_list(get(event, "event.category")) == ["authentication"]
    assert get(event, "event.action") == "ssh_login"

    for field, expected in SSHD_EXPECTED[index].items():
        actual = get(event, field)
        if expected is None:
            assert actual is None, f"{field} should be absent, got {actual!r}"
        else:
            assert actual == expected, f"{field}: expected {expected!r}, got {actual!r}"
            if isinstance(expected, int):
                assert isinstance(actual, int) and not isinstance(actual, bool), f"{field} is not an integer"


@pytest.mark.parametrize("index", sorted(UNPARSED))
def test_other_lines_are_tagged_unparsed(events_by_line, index):
    event = events_by_line[index]
    _check_common(event, index)

    assert "_sshd_unparsed" in as_list(event.get("tags"))
    assert get(event, "event.category") is None
    for field in ("event.kind", "event.action", "event.outcome", "event.reason",
                  "user.name", "source.ip", "source.port", "system.auth.ssh.method"):
        assert get(event, field) is None, f"{field} should be absent on an unparsed line"
    for field, expected in UNPARSED[index].items():
        assert get(event, field) == expected


# End to end for rules/sshd_invalid_user_login.yml (R-03): raw sshd line -> pipeline -> rule.
from sigma_match import rule_matches  # noqa: E402

RULE_INVALID_USER = ROOT / "rules" / "sshd_invalid_user_login.yml"
SAMPLES = Path(__file__).resolve().parent / "samples"


def _lines(path):
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_invalid_user_positive_sample_fires_rule():
    sample = SAMPLES / "sshd_invalid_user_positive.log"
    events = run_pipeline(sample)
    assert len(events) == len(_lines(sample)), f"expected {len(_lines(sample))} events, got {len(events)}"
    quiet = [get(e, "event.original") for e in events if not rule_matches(RULE_INVALID_USER, e)]
    assert not quiet, f"rule did not fire on: {quiet}"


def test_invalid_user_negative_sample_does_not_fire_rule():
    sample = SAMPLES / "sshd_invalid_user_negative.log"
    events = run_pipeline(sample)
    assert len(events) == len(_lines(sample)), f"expected {len(_lines(sample))} events, got {len(events)}"
    fired = [get(e, "event.original") for e in events if rule_matches(RULE_INVALID_USER, e)]
    assert not fired, f"rule fired on: {fired}"


# End to end for rules/sshd_root_password_login.yml (R-03, R-07): raw sshd line -> pipeline -> rule.
RULE_ROOT_PASSWORD = ROOT / "rules" / "sshd_root_password_login.yml"


def test_root_password_positive_sample_fires_rule():
    sample = SAMPLES / "sshd_root_password_positive.log"
    events = run_pipeline(sample)
    assert len(events) == len(_lines(sample)), f"expected {len(_lines(sample))} events, got {len(events)}"
    quiet = [get(e, "event.original") for e in events if not rule_matches(RULE_ROOT_PASSWORD, e)]
    assert not quiet, f"rule did not fire on: {quiet}"


def test_root_password_negative_sample_does_not_fire_rule():
    sample = SAMPLES / "sshd_root_password_negative.log"
    events = run_pipeline(sample)
    assert len(events) == len(_lines(sample)), f"expected {len(_lines(sample))} events, got {len(events)}"
    fired = [get(e, "event.original") for e in events if rule_matches(RULE_ROOT_PASSWORD, e)]
    assert not fired, f"rule fired on: {fired}"
