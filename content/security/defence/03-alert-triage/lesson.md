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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **alert** | a notice raised by a detection rule |
| **triage** | sorting incoming alerts so the most important are handled first |
| **analyst** | the person who reads and investigates alerts |
| **queue** | the list of alerts waiting for an analyst |
| **alert fatigue** | so many alerts that people stop reading them carefully and miss real ones |
| **noise** | alerts that do not matter |
| **deduplicate** (dedupe) | collapse identical alerts into one entry with a count |
| **source** | where an alert came from: an address or a machine name |
| **kind** | what the alert is about, such as `failed-login` or `data-exfil` |
| **severity** | how serious an alert is: low, medium, high, critical |
| **prioritise** | order by importance, not by arrival time |
| **exfiltration** (exfil) | data being copied out of the organisation |
| **stable sort** | a sort that keeps the original order of items that compare equal |
| **correlation** | linking related alerts into one incident |
| **suppression** | muting alerts already known to be harmless |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sort \| uniq -c \| sort -nr` | the shell version of dedupe: counts identical lines, most common first |
| `python triage.py` | runs your program: dedupes three alerts and picks the most urgent |

### Python names

| Name | What it does |
|---|---|
| `RANK` | given to you: a dict from severity to a number, higher is worse |
| `key = (a["source"], a["kind"])` | a tuple used as a dict key |
| `counts.get(key, 0) + 1` | the count so far (0 the first time), plus one |
| `sorted(alerts, key=lambda a: RANK[a["severity"]], reverse=True)` | sorted by severity number, highest first |
| `reverse=True` | largest first; Python's sort stays stable even with this |
| `by_severity(alerts)[0]` | the first item of the sorted list |
| `if not alerts:` | the list is empty |

---

A working detection pipeline has the opposite problem to having no detection
at all: it produces **too many alerts**. The same scanner trips a rule a
thousand times, and low-priority **noise** buries the one critical alert that
matters. **Triage** turns that flood into a short, ordered list a person can
act on.

This is not a small matter. **Alert fatigue**, where analysts see so many
alerts that real ones slip past, is one of the main reasons breaches go
unnoticed.

## Move 1: deduplicate

A hundred identical alerts from one source are one fact, not a hundred.
Collapse alerts that share a **source** and a **kind** into one entry with a
count:

```text
before:                                   after:
10.0.0.9  failed-login  low               (10.0.0.9, failed-login)  x 500
10.0.0.9  failed-login  low               (db01,     data-exfil)    x 1
...  (498 more)
db01      data-exfil    critical
```

A screen of noise becomes one line, "500 failed logins from 10.0.0.9", and
the one alert that was hiding underneath it is now visible.

## Move 2: prioritise

Not all alerts are equal. A `critical` one (data being copied out right now)
must come before a `low` one (a single blocked scan), whatever order they
arrived in. Sort by **severity**, highest first, and the analyst's attention
goes where it belongs. The first item is the **most urgent**, the one to look
at now.

Among alerts of the **same** severity, keep the order they arrived in. That
preserves the timeline within each priority band. A **stable sort** does
this, and Python's `sorted` is always stable, even with `reverse=True`.

## The rest of a real platform

Real platforms add more:

- **correlation**: linking related alerts (a scan, then a login, then a large
  transfer from the same address) into one incident, as in Forensics lesson 6;
- **suppression**: muting alerts known to be harmless, such as the company's
  own vulnerability scanner.

But deduplicating and prioritising are the two moves that do most to keep a
queue manageable.

## Your turn

`RANK` (severity to a number, higher is worse) is given to you. In
`triage.py`, each alert is a dict with `source`, `kind` and `severity`:

- `dedupe(alerts)`: a dict from `(source, kind)` to the number of such
  alerts.
- `by_severity(alerts)`: the alerts sorted most severe first, keeping arrival
  order among equals.
- `most_urgent(alerts)`: the single most severe alert, or `None` if there are
  none.

Run it:

```text
deduped: {('10.0.0.9', 'failed-login'): 2, ('db01', 'data-exfil'): 1}
most urgent: {'source': 'db01', 'kind': 'data-exfil', 'severity': 'critical'}
```

## Check yourself

1. What is alert fatigue?
   *So many alerts that real ones are missed.*
2. 500 identical failed-login alerts from one address. How should they
   appear after triage?
   *As one entry with a count of 500.*
3. A `low` alert arrived before a `critical` one. Which comes first after
   triage?
   *The critical one.*
4. Why keep arrival order among alerts of the same severity?
   *It preserves the timeline within each priority band.*
5. What is suppression?
   *Muting alerts known to be harmless.*
