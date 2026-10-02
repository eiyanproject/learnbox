---
title: Alert triage
summary: A detection pipeline produces more alerts than anyone can read. Triage is collapsing the noise and surfacing what matters first.
order: 3
files: [triage.py]
run: python triage.py
hints:
  - "`dedupe`: collapse alerts that share the same `(source, kind)` into a count. Return a dict keyed by that pair."
  - "`by_severity`: sort alerts from most to least severe using the `RANK` mapping (critical highest). Keep the original order among equals (a stable sort does this)."
  - "`most_urgent`: the single highest-severity alert, or None if there are none."
  - "Each alert is a dict with `source`, `kind` and `severity`."
---

A working detection pipeline has the opposite problem to no detection at all:
it produces **too many alerts**. The same scanner trips a rule a thousand times;
low-priority noise buries the one critical alert that matters. **Triage** is the
discipline of turning that flood into a short, ordered list a human can act on -
and alert fatigue, where real alerts are missed in the noise, is a leading cause
of breaches going unnoticed.

## Two moves

**Deduplicate.** A hundred identical alerts from one source are one fact, not a
hundred. Collapsing alerts that share a source and kind into a single entry with
a count turns a screen of noise into one line: "500 failed logins from
10.0.0.9".

**Prioritise.** Not all alerts are equal. A `critical` (active data theft) must
rise above a `low` (a single blocked scan) regardless of what order they
arrived in. Sorting by severity puts the analyst's attention where it belongs,
and the most urgent alert is the one they should see first.

Real platforms add correlation (linking related alerts into one incident) and
suppression (muting known-benign noise), but dedupe and prioritise are the two
that do the most to make a queue survivable.

## Your turn

`RANK` (severity to a number, higher is worse) is provided. In `triage.py`
(each alert is a dict with `source`, `kind`, `severity`):

- `dedupe(alerts)` - a dict from `(source, kind)` to the number of such alerts
- `by_severity(alerts)` - the alerts sorted most-severe first, stable among
  equals
- `most_urgent(alerts)` - the single most severe alert, or `None`
