"""Record what Shodan already knows about your own public IP (RISK-REGISTER R-14, feeds R-05).

Query only an address you own or are authorised to assess. OWN_PUBLIC_IP is read
from the environment at run time and is never written anywhere: the snapshot keeps
only the fields that show whether the exposure changed, without the address.
One host() call per run; the free tier rate-limits loops. Lab 7 diffs these snapshots.
"""
import json
import os
from datetime import date
from pathlib import Path


def snapshot(host):
    """Keep the comparable fields, without the IP. host=None means Shodan has not indexed it."""
    if host is None:
        return {"indexed": False, "ports": [], "org": None, "last_update": None}
    return {
        "indexed": True,
        "ports": sorted(host.get("ports", [])),
        "org": host.get("org"),
        "last_update": host.get("last_update"),
    }


def main():
    import shodan

    api = shodan.Shodan(os.environ["SHODAN_KEY"])
    try:
        host = api.host(os.environ["OWN_PUBLIC_IP"])
    except shodan.APIError as err:
        if "No information available" not in str(err):
            raise SystemExit(f"Shodan: {err}")
        host = None  # not indexed: a valid finding and a baseline for Lab 7
    snap = snapshot(host)
    out = Path("exposure") / f"{date.today()}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(snap, indent=2) + "\n")
    print(json.dumps(snap, indent=2))


if __name__ == "__main__":
    main()
