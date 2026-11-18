"""Observability checks (RISK-REGISTER R-09): alert rules, Prometheus and Alertmanager config.

The promtool and amtool checks run inside the pinned images from compose.yaml, offline,
and are skipped where Docker is unavailable; the port check needs no Docker.
"""
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
OBS = ROOT / "observability"
SERVICES = yaml.safe_load((ROOT / "compose.yaml").read_text())["services"]
OBSERVABILITY_SERVICES = ["prometheus", "alertmanager", "grafana", "logstash-exporter", "opensearch-exporter"]

needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="needs Docker")


def run_tool(service, tool, config_dir, *args):
    """Run promtool/amtool from the service's pinned image with config_dir mounted read-only at /cfg."""
    cmd = [
        "docker", "run", "--rm", "--network", "none", "--entrypoint", tool,
        "--mount", f"type=bind,source={config_dir},target=/cfg,readonly",
        SERVICES[service]["image"], *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


@needs_docker
def test_alert_rules_unit_tests_pass():
    result = run_tool("prometheus", "promtool", OBS / "prometheus", "test", "rules", "/cfg/alerts_test.yml")
    assert result.returncode == 0, result.stdout + result.stderr


@needs_docker
def test_prometheus_config_is_valid():
    result = run_tool("prometheus", "promtool", OBS / "prometheus", "check", "config", "/cfg/prometheus.yml")
    assert result.returncode == 0, result.stdout + result.stderr


@needs_docker
def test_alertmanager_config_is_valid():
    result = run_tool("alertmanager", "amtool", OBS / "alertmanager", "check-config", "/cfg/alertmanager.yml")
    assert result.returncode == 0, result.stdout + result.stderr


def test_observability_services_publish_on_localhost_only():
    for name in OBSERVABILITY_SERVICES:
        for port in SERVICES[name].get("ports", []):
            assert str(port).startswith("127.0.0.1:"), f"{name} publishes {port} beyond localhost"
