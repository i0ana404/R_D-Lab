"""Unit tests for the MISP lookup writer (RISK-REGISTER R-08, R-10). Need no MISP server."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import yaml

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("misp_pull", ROOT / "scripts/misp_pull.py")
misp_pull = importlib.util.module_from_spec(spec)
spec.loader.exec_module(misp_pull)


def attr(value, event_id, category="Network activity"):
    return SimpleNamespace(value=value, event_id=event_id, category=category)


def test_lookup_is_deduplicated_sorted_and_valid_yaml():
    text = misp_pull.render([attr("198.51.100.9", 7), attr("192.0.2.1", 3), attr("198.51.100.9", 9)])
    assert yaml.safe_load(text) == {
        "192.0.2.1": "misp:3:Network activity",
        "198.51.100.9": "misp:7:Network activity",
    }
    assert text.splitlines()[0].startswith('"192.0.2.1"')


def test_empty_feed_renders_nothing():
    assert misp_pull.render([]) == ""


def test_tls_verification_is_never_disabled(monkeypatch):
    monkeypatch.delenv("MISP_CA", raising=False)
    assert misp_pull.tls_verify() is True
    monkeypatch.setenv("MISP_CA", "")
    assert misp_pull.tls_verify() is True
    monkeypatch.setenv("MISP_CA", "/path/to/root_ca.crt")
    assert misp_pull.tls_verify() == "/path/to/root_ca.crt"
