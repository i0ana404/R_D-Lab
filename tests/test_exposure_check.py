"""Unit tests for the InternetDB exposure snapshot (RISK-REGISTER R-14). Make no network call."""
import importlib.util
import io
import json
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("exposure_check", ROOT / "scripts/exposure_check.py")
exposure_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exposure_check)

RECORD = {"ip": "198.51.100.20", "ports": [443, 22], "hostnames": ["198-51-100-20.example.net"],
          "cpes": ["cpe:/a:openbsd:openssh"], "vulns": ["CVE-2024-6387"], "tags": ["self-signed"]}


def test_snapshot_keeps_only_comparable_fields_with_sorted_ports_and_no_ip():
    snap = exposure_check.snapshot(RECORD)
    assert snap == {"indexed": True, "ports": [22, 443], "vulns": ["CVE-2024-6387"], "tags": ["self-signed"]}
    assert "198.51.100.20" not in json.dumps(snap)
    assert "198-51-100-20" not in json.dumps(snap)


def test_no_data_gives_an_empty_baseline():
    empty = {"indexed": False, "ports": [], "vulns": [], "tags": []}
    assert exposure_check.snapshot(None) == empty
    assert exposure_check.snapshot({"detail": "No information available"}) == empty


def test_fetch_treats_404_as_not_indexed_and_hides_the_address(monkeypatch):
    def not_found(url, timeout):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO(b"{}"))
    monkeypatch.setattr(exposure_check.urllib.request, "urlopen", not_found)
    assert exposure_check.fetch("198.51.100.20") is None

    def server_error(url, timeout):
        raise urllib.error.HTTPError(url, 500, "Server Error", {}, io.BytesIO(b"{}"))
    monkeypatch.setattr(exposure_check.urllib.request, "urlopen", server_error)
    try:
        exposure_check.fetch("198.51.100.20")
    except SystemExit as exc:
        assert "198.51.100.20" not in str(exc)
    else:
        raise AssertionError("expected SystemExit on HTTP 500")


def test_fetch_sends_its_own_user_agent(monkeypatch):
    seen = {}

    def capture(req, timeout):
        seen["ua"] = req.get_header("User-agent")
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b"{}"))
    monkeypatch.setattr(exposure_check.urllib.request, "urlopen", capture)
    exposure_check.fetch("198.51.100.20")
    assert seen["ua"] and not seen["ua"].startswith("Python-urllib")
