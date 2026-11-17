"""The stack's Logstash pipeline (file input, sshd filter, OpenSearch output) is valid config (R-03, R-09).

Runs logstash --config.test_and_exit on logstash/pipeline/ inside the pinned image. No network,
and a placeholder password: the check only parses the configuration and connects to nothing.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from test_sshd_ecs import logstash_image

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "logstash" / "pipeline"
IOC_DICTIONARY = ROOT / "tests" / "samples" / "ioc_ip_test.yml"


def test_stack_pipeline_config_is_valid():
    if shutil.which("docker") is None:
        pytest.skip("docker is not on PATH; the Logstash config test needs it")
    image = logstash_image()
    if not image:
        pytest.skip("no LOGSTASH_IMAGE in the environment, .env or .env.example")
    cmd = [
        "docker", "run", "--rm", "--network", "none",
        "-e", "LS_JAVA_OPTS=-Xms256m -Xmx256m",
        "-e", "OPENSEARCH_INITIAL_ADMIN_PASSWORD=unused",
        "--mount", f"type=bind,source={PIPELINE},target=/usr/share/logstash/pipeline,readonly",
        # Dictionary for 30-enrich-ioc.conf (test copy, in place of the git-ignored enrich/ioc_ip.yml).
        "--mount", f"type=bind,source={IOC_DICTIONARY},target=/enrich/ioc_ip.yml,readonly",
        image, "--config.test_and_exit", "-f", "/usr/share/logstash/pipeline/",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output[-4000:]
    assert "Configuration OK" in output or "Validation Result: OK" in output, output[-4000:]
