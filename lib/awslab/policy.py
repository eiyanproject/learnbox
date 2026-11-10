"""A small IAM policy evaluator, for checks that ask "could this identity do X?".

The emulator stores policies but has no policy simulator, so the AWS lessons
decide access here. It follows the core of AWS's evaluation logic:

  * an explicit Deny in any statement that matches wins;
  * otherwise an Allow that matches allows;
  * otherwise the request is implicitly denied.

Action and Resource patterns use `*` (any run of characters) and `?` (one
character); actions match case-insensitively, as AWS does. NotAction and
NotResource invert a statement's match.

Condition blocks are judged only when the caller passes a request context
(`decide(..., context={"aws:RequestedRegion": "eu-west-1"})`), for the
common operators: String*, Arn*, Bool and Null, each with ...IfExists.
Without a context, a statement with a Condition is reported, not guessed at.
An operator outside that list raises, rather than being guessed at.

SCPs are evaluated by `scp_decide`: every level from the root down to the
account must allow, and a Deny at any level wins.

Deliberately not modelled: permission boundaries, session policies and
resource policies. Lessons that need those check the documents directly.
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


_NEGATED = {"StringNotEquals", "StringNotEqualsIgnoreCase", "StringNotLike", "ArnNotEquals", "ArnNotLike"}
_OPERATORS = _NEGATED | {"StringEquals", "StringEqualsIgnoreCase", "StringLike", "ArnEquals", "ArnLike", "Bool", "Null"}


def _value_matches(op: str, want: str, got: str) -> bool:
    if op in ("StringEquals", "StringNotEquals", "ArnEquals", "ArnNotEquals"):
        return want == got
    if op in ("StringEqualsIgnoreCase", "StringNotEqualsIgnoreCase"):
        return want.lower() == got.lower()
    if op in ("StringLike", "StringNotLike", "ArnLike", "ArnNotLike"):
        return _match(want, got, fold=False)
    if op == "Bool":
        return want.lower() == got.lower()
    raise ValueError(op)


def condition_holds(cond: dict, context: dict) -> bool:
    """Whether a statement's Condition block holds for a request context.
    Keys are matched case-insensitively, as AWS does; values in one condition
    are ORed, separate conditions ANDed. A missing key makes a negated
    operator true and any other operator false (unless ...IfExists)."""
    ctx = {k.lower(): str(v) for k, v in context.items()}
    for raw_op, pairs in cond.items():
        op, if_exists = (raw_op[:-8], True) if raw_op.endswith("IfExists") else (raw_op, False)
        if op not in _OPERATORS:
            raise ValueError(f"condition operator {raw_op} is not modelled")
        for key, wants in pairs.items():
            got = ctx.get(key.lower())
            wants = [str(w) for w in as_list(wants)]
            if op == "Null":
                absent = got is None
                if not any((w.lower() == "true") == absent for w in wants):
                    return False
                continue
            if got is None:
                if if_exists or op in _NEGATED:
                    continue
                return False
            hit = any(_value_matches(op, w, got) for w in wants)
            if hit == (op in _NEGATED):
                return False
    return True


def decide(docs: Iterable, action: str, resource: str = "*", context: dict | None = None) -> Decision:
    """Evaluate identity policies for one action on one resource. With a
    request context, Condition blocks are judged; without one, statements
    that have them are set aside in Decision.conditional."""
    allow = False
    conditional = []
    for doc in docs:
        for st in statements(doc):
            if not statement_matches(st, action, resource):
                continue
            if st.get("Condition"):
                if context is None:
                    conditional.append(st)
                    continue
                if not condition_holds(st["Condition"], context):
                    continue
            if st.get("Effect") == "Deny":
                return Decision(EXPLICIT_DENY, conditional)
            if st.get("Effect") == "Allow":
                allow = True
    return Decision(ALLOW if allow else IMPLICIT_DENY, conditional)


def scp_decide(levels: Iterable[Iterable], action: str, resource: str = "*", context: dict | None = None) -> Decision:
    """Evaluate SCPs. `levels` holds the policies attached at each level of
    the path from the root to the account (root, each OU, the account). A
    request passes only if every level allows it; a Deny anywhere wins."""
    result = ALLOW
    for docs in levels:
        d = decide(docs, action, resource, context if context is not None else {})
        if d.result == EXPLICIT_DENY:
            return d
        if d.result == IMPLICIT_DENY:
            result = IMPLICIT_DENY
    return Decision(result)


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
