"""Evaluate a Sigma rule against ECS events in Python, so CI can test rule logic.

Supports what this course uses: field lists (OR), the modifiers contains,
startswith, endswith and re, and conditions built from selection names with
and, or, not and parentheses. Matching follows the OpenSearch query the rule
converts to: plain values ignore case, re must match the whole value.
"""
import re
from pathlib import Path

import yaml


def _values(event, dotted):
    """Every value at a dotted ECS path, walking into lists."""
    found = [event]
    for key in dotted.split("."):
        nxt = []
        for node in found:
            items = node if isinstance(node, list) else [node]
            nxt += [i[key] for i in items if isinstance(i, dict) and key in i]
        found = nxt
    flat = []
    for v in found:
        flat += v if isinstance(v, list) else [v]
    return [str(v) for v in flat]


def _field_ok(event, spec, wanted):
    field, *mods = spec.split("|")
    wanted = wanted if isinstance(wanted, list) else [wanted]
    for have in _values(event, field):
        for w in map(str, wanted):
            if "re" in mods and re.fullmatch(w, have, re.DOTALL):
                return True
            h, w2 = have.lower(), w.lower()
            if "contains" in mods and w2 in h:
                return True
            if "startswith" in mods and h.startswith(w2):
                return True
            if "endswith" in mods and h.endswith(w2):
                return True
            if not mods and h == w2:
                return True
    return False


def _selection_ok(event, selection):
    return all(_field_ok(event, k, v) for k, v in selection.items())


def rule_matches(rule_path, event):
    det = yaml.safe_load(Path(rule_path).read_text())["detection"]
    tokens = re.findall(r"\(|\)|[\w.]+", det["condition"])
    pos = 0

    def expr():
        nonlocal pos
        val = term()
        while pos < len(tokens) and tokens[pos] == "or":
            pos += 1
            val = term() or val
        return val

    def term():
        nonlocal pos
        val = factor()
        while pos < len(tokens) and tokens[pos] == "and":
            pos += 1
            val = factor() and val
        return val

    def factor():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "not":
            return not factor()
        if tok == "(":
            val = expr()
            pos += 1
            return val
        return _selection_ok(event, det[tok])

    return expr()
