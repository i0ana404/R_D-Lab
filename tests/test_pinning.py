"""Every image this repo builds or runs is pinned by digest (RISK-REGISTER: supply chain).

A floating tag such as nginx:1.27-alpine can change under you between two builds.
A digest cannot. Images that come from .env (${VAR}) are pinned there instead.
"""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")


def dockerfiles():
    return sorted(p for p in ROOT.rglob("Dockerfile*") if ".git" not in p.parts)


@pytest.mark.parametrize("path", dockerfiles(), ids=lambda p: str(p.relative_to(ROOT)))
def test_dockerfile_base_images_are_pinned_by_digest(path):
    froms = [line.split()[1] for line in path.read_text().splitlines()
             if line.strip().upper().startswith("FROM ")]
    assert froms, f"{path} has no FROM line"
    for image in froms:
        assert DIGEST.search(image), f"{path}: {image} is not pinned by a real digest"


def test_compose_images_are_pinned_by_digest_or_come_from_env():
    compose = ROOT / "compose.yaml"
    if not compose.exists():
        pytest.skip("no compose.yaml in this repository")
    services = yaml.safe_load(compose.read_text()).get("services", {})
    for name, svc in services.items():
        image = svc.get("image", "")
        if not image or image.startswith("${"):
            continue
        assert DIGEST.search(image), f"service {name}: {image} is not pinned by digest"
