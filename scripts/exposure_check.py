"""Record what Shodan's InternetDB already knows about your own public IP (RISK-REGISTER R-14, feeds R-05).

Query only an address you own or are authorised to assess. The Shodan host API returns
403 on the free plan (it needs a paid membership), so this uses Shodan InternetDB: free
for non-commercial use, no API key, data refreshed weekly. OWN_PUBLIC_IP is read from
the environment at run time and is never written or printed: the snapshot keeps only
the fields that show whether the exposure changed (hostnames are left out because ISP
hostnames usually embed the address). One request per run. Lab 7 diffs these snapshots.
"""
import json
import os
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

URL = "https://internetdb.shodan.io/{ip}"
# InternetDB answers 403 to Python's default "Python-urllib/3.x" User-Agent.
HEADERS = {"User-Agent": "R_D-Lab-exposure-check/1.0", "Accept": "application/json"}


def snapshot(record):
    """Keep the comparable fields, without the IP. record=None means InternetDB has no data."""
    if not record or "ports" not in record:
        return {"indexed": False, "ports": [], "vulns": [], "tags": []}
    return {
        "indexed": True,
        "ports": sorted(record.get("ports", [])),
        "vulns": sorted(record.get("vulns", [])),
        "tags": sorted(record.get("tags", [])),
    }


def fetch(ip):
    """One InternetDB lookup. 404 means not indexed; errors never echo the address."""
    try:
        req = urllib.request.Request(URL.format(ip=ip), headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise SystemExit(f"InternetDB: HTTP {err.code}") from None
    except urllib.error.URLError as err:
        raise SystemExit(f"InternetDB: {err.reason}") from None


def main():
    snap = snapshot(fetch(os.environ["OWN_PUBLIC_IP"]))
    out = Path("exposure") / f"{date.today()}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(snap, indent=2) + "\n")
    print(json.dumps(snap, indent=2))


if __name__ == "__main__":
    main()
