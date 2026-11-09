"""A small IAM policy evaluator, for checks that ask "could this identity do X?".

The emulator stores policies but has no policy simulator, so the AWS lessons
decide access here. It follows the core of AWS's evaluation logic:

  * an explicit Deny in any statement that matches wins;
  * otherwise an Allow that matches allows;
  * otherwise the request is implicitly denied.

Action and Resource patterns use `*` (any run of characters) and `?` (one
character); actions match case-insensitively, as AWS does. NotAction and
NotResource invert a statement's match.

Deliberately not modelled: Condition blocks (a statement with one is
reported, not guessed at - see `decide`), permission boundaries, SCPs,
session policies and resource policies. Lessons that need those check the
documents directly.
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from typing import Iterable

ALLOW = "allowed"
EXPLICIT_DENY = "explicitDeny"
IMPLICIT_DENY = "implicitDeny"


def as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def load(doc) -> dict:
    """A policy document from a dict, a JSON string, or a URL-encoded string."""
    if isinstance(doc, dict):
        return doc
    from urllib.parse import unquote

    text = doc if doc.lstrip().startswith("{") else unquote(doc)
    return json.loads(text)


def statements(doc) -> list[dict]:
    return as_list(load(doc).get("Statement"))


def _match(pattern: str, value: str, fold: bool) -> bool:
    if fold:
        pattern, value = pattern.lower(), value.lower()
    # fnmatch's [] classes are not IAM syntax; escape them.
    pattern = pattern.replace("[", "[[]")
    return fnmatch.fnmatchcase(value, pattern)


def _any(patterns: Iterable[str], value: str, fold: bool) -> bool:
    return any(_match(p, value, fold) for p in patterns)


def statement_matches(st: dict, action: str, resource: str) -> bool:
    if "Action" in st:
        hit = _any(as_list(st["Action"]), action, fold=True)
    else:
        hit = not _any(as_list(st.get("NotAction")), action, fold=True)
    if not hit:
        return False
    if "Resource" in st:
        return _any(as_list(st["Resource"]), resource, fold=False)
    if "NotResource" in st:
        return not _any(as_list(st["NotResource"]), resource, fold=False)
    return True  # trust policies have no Resource


@dataclass
class Decision:
    result: str
    conditional: list[dict] = field(default_factory=list)  # matching statements we could not judge

    @property
    def allowed(self) -> bool:
        return self.result == ALLOW


def decide(docs: Iterable, action: str, resource: str = "*") -> Decision:
    """Evaluate identity policies for one action on one resource."""
    allow = False
    conditional = []
    for doc in docs:
        for st in statements(doc):
            if not statement_matches(st, action, resource):
                continue
            if st.get("Condition"):
                conditional.append(st)
                continue
            if st.get("Effect") == "Deny":
                return Decision(EXPLICIT_DENY, conditional)
            if st.get("Effect") == "Allow":
                allow = True
    return Decision(ALLOW if allow else IMPLICIT_DENY, conditional)


def wildcards(doc) -> list[str]:
    """Allow statements that grant every action or every resource - the two
    things least privilege rules out."""
    found = []
    for st in statements(doc):
        if st.get("Effect") != "Allow":
            continue
        for a in as_list(st.get("Action")):
            if a == "*" or a.endswith(":*"):
                found.append(f"Action {a}")
        for r in as_list(st.get("Resource")):
            if r == "*":
                found.append("Resource *")
    return found
