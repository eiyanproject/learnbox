---
title: "Capstone: working an incident"
summary: Turning a pile of indicators into a classified incident with the right containment action and the phases worked in the right order.
order: 6
files: [incident.py]
run: python incident.py
hints:
  - "`severity`: map the worst indicator present to a severity. `SEVERITY` gives each indicator's level; return the highest by `RANK`, or 'none' if there are no indicators."
  - "`containment`: look the severity up in `CONTAINMENT` for the action to take; an unknown or 'none' severity means 'monitor'."
  - "`PHASES` is the canonical order; `next_phase` returns the phase after the current one, or None if the current one is the last."
  - "`is_valid_order`: a response is valid only if its phases appear in the same relative order as PHASES - you cannot eradicate before you contain."
---

The sections before this each produced one piece of an investigation: a
detection, an alert, a timeline, a baseline diff. **Incident response** is the
discipline that runs the whole thing - from a confusing pile of indicators to a
classified incident, the right immediate action, and an orderly recovery. This
capstone ties the defensive section together.

## Classify, then contain

First, **how bad is it?** The indicators present decide the severity - active
data exfiltration or ransomware is `critical`, a compromised credential is
`high`, a blocked scan is `low`. You classify by the **worst** thing you see,
because the response must match the most serious indicator, not the average one.

Severity then drives the **containment** action - the immediate step to stop the
bleeding before anything else: isolate the host for a critical, disable the
account for a credential compromise, keep monitoring for the merely noisy.
Containment comes first because every minute of delay is more damage.

## The phases, in order

Incident response follows a fixed sequence. This is the SANS model, whose first
phase - **preparation**: playbooks, logging and contacts in place *before*
anything happens - is the one done before an incident starts. Once it has
started, the order is not optional:

```text
identify  ->  contain  ->  eradicate  ->  recover  ->  lessons learned
```

You cannot eradicate what you have not contained (it spreads while you work),
and you cannot recover onto a system you have not cleaned (you restore the
compromise with it). Getting the order right is as much the job as any single
step - a response that recovers before eradicating reinfects itself.

## Your turn

`SEVERITY`, `RANK`, `CONTAINMENT` and `PHASES` are provided. In `incident.py`:

- `severity(indicators)` - the worst severity among the indicators, or `"none"`
- `containment(sev)` - the immediate action for that severity
- `next_phase(current)` - the phase after `current`, or `None` if it is last
- `is_valid_order(phases)` - whether the phases are in the canonical order
