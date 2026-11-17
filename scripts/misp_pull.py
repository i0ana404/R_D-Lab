"""Pull IP indicators from MISP into the Logstash lookup file (RISK-REGISTER R-08, R-10).

Feed lifecycle in one place: only attributes flagged to_ids (trust), minus
anything on a MISP warninglist (known benign), seen within MISP_MAX_AGE
(ageing out), one line per IP (deduplicated), sorted so diffs stay small.
TLS verification is never switched off: MISP_CA points at the internal CA,
otherwise the system trust store is used.
"""
import json
import os
import sys
from pathlib import Path

OUT = Path("enrich/ioc_ip.yml")


def tls_verify():
    """Return the CA bundle from MISP_CA, or True for the system trust store. Never False."""
    return os.environ.get("MISP_CA") or True


def render(attrs):
    """Return the translate dictionary: one "ip": "misp:<event>:<category>" line per IP."""
    seen = {}
    for a in attrs:
        seen.setdefault(a.value, f"misp:{a.event_id}:{a.category}")
    return "".join(f"{json.dumps(ip)}: {json.dumps(tag)}\n" for ip, tag in sorted(seen.items()))


def main():
    import pymisp

    misp = pymisp.PyMISP(os.environ["MISP_URL"], os.environ["MISP_KEY"], ssl=tls_verify())
    attrs = misp.search(
        controller="attributes",
        type_attribute=["ip-dst", "ip-src"],
        to_ids=True,
        enforce_warninglist=True,
        timestamp=os.environ.get("MISP_MAX_AGE", "30d"),
        pythonify=True,
    )
    text = render(attrs)
    if not text:
        sys.exit("MISP returned no indicators; the previous lookup file stays in place.")
    OUT.parent.mkdir(exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(text)
    tmp.replace(OUT)  # atomic, so Logstash never reads a half-written file
    print(f"{len(text.splitlines())} unique indicators written to {OUT}")


if __name__ == "__main__":
    main()
