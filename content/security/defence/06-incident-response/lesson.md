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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **incident response** (IR) | the organised way of handling a security incident from first sign to recovery |
| **indicator** (indicator of compromise) | a sign that something is wrong: a scan, a stolen login, data leaving |
| **classify** | decide how serious an incident is |
| **severity** | that seriousness: none, low, medium, high, critical |
| **worst indicator** | the most serious sign present; it sets the severity |
| **ransomware** | malware that encrypts files and demands payment |
| **credential compromise** | an attacker has someone's password or key |
| **containment** | the immediate step that stops the damage spreading |
| **isolate a host** | cut a machine off from the network, while keeping it running for evidence |
| **disable an account** | stop it from signing in, without deleting it |
| **phase** | one stage of the response, done in a fixed order |
| **preparation** | the work done before any incident: plans, logging, contacts |
| **identify** (detection and analysis) | confirm what is happening and how far it reaches |
| **eradicate** | remove the attacker's access and tools: malware, backdoors, stolen keys |
| **recover** | bring systems back into normal service, clean |
| **lessons learned** | the review afterwards: what to change so it does not happen again |
| **playbook** | written steps for handling one kind of incident |
| **SANS**, **NIST** | organisations whose incident response models are widely used; their phases are nearly the same |
| **reinfection** | the attacker coming back because the system was restored before it was cleaned |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python incident.py` | runs your program: classifies three indicators and checks a phase order |

### Python names

| Name | What it does |
|---|---|
| `SEVERITY` | given to you: a dict from indicator to severity |
| `RANK` | given to you: a dict from severity to a number, higher is worse |
| `CONTAINMENT` | given to you: a dict from severity to the immediate action |
| `PHASES` | given to you: the phases in their required order |
| `SEVERITY.get(ind, "none")` | the indicator's severity, or `"none"` if it is unknown |
| `RANK[level] > RANK[worst]` | this level is worse than the worst seen so far |
| `PHASES.index(current)` | the position of a phase in the list |
| `PHASES[i + 1] if i + 1 < len(PHASES) else None` | the next phase, or `None` after the last |
| `indices == sorted(indices)` | the positions only ever go up: the order is right |

---

Each earlier lesson in this section produced one piece of an investigation:
a hardened config, a detection, a triaged alert, an integrity check, an access
review. **Incident response** is the discipline that runs the whole thing:
from a confusing pile of **indicators**, to a classified incident, to the
right immediate action, to an orderly recovery. This capstone ties the
defensive section together.

## Step 1: classify by the worst indicator

First question: **how bad is it?** The indicators present decide the
**severity**:

| Indicator | Severity |
|---|---|
| data being copied out (exfiltration), ransomware | critical |
| a stolen password or key, malware found | high |
| a port scan, some failed logins | low |

Classify by the **worst** indicator you see, not the average. A port scan and
a data theft together are a data theft. The response has to match the most
serious thing happening.

## Step 2: contain

The severity decides the **containment** action: the immediate step to stop
the damage before anything else.

| Severity | Contain by |
|---|---|
| critical | isolate the host: cut it off from the network |
| high | disable the affected account |
| low, none | keep monitoring |

Containment comes first because every minute of delay means more damage.
Note what it is **not**: switching the machine off or deleting the account.
An isolated machine keeps its memory and logs for the investigation; a
disabled account keeps its history.

## The phases, in order

Incident response follows a fixed sequence. This lesson uses the SANS model;
NIST's is nearly the same. Its first phase, **preparation** (playbooks,
logging and contact lists in place), happens **before** any incident. Once one
has started, the order is not optional:

```text
identify  ->  contain  ->  eradicate  ->  recover  ->  lessons learned
```

1. **Identify**: confirm what is happening and how far it reaches.
2. **Contain**: stop it spreading.
3. **Eradicate**: remove the attacker's access: malware, backdoors, stolen
   keys, new accounts.
4. **Recover**: bring systems back into service, clean.
5. **Lessons learned**: what to change so it does not happen again.

Why the order matters:

- You cannot eradicate what you have not contained: it spreads while you work.
- You cannot recover onto a system you have not cleaned: you restore the
  attacker's access along with everything else, and **reinfection** follows.

A phase may be skipped in a small incident, but none may come before one that
should precede it. Getting the order right is as much the job as any single
step.

## Your turn

`SEVERITY`, `RANK`, `CONTAINMENT` and `PHASES` are given to you. In
`incident.py`:

- `severity(indicators)`: the worst severity among the indicators, by
  `RANK`. Indicators not in `SEVERITY` are ignored; with none left, it is
  `"none"`.
- `containment(sev)`: the immediate action for that severity (`"monitor"` for
  anything unknown).
- `next_phase(current)`: the phase after `current`, or `None` if it is the
  last.
- `is_valid_order(phases)`: whether the phases appear in the same order as in
  `PHASES`. Phases may be skipped, but none may come before one that precedes
  it in `PHASES`.

Run it:

```text
severity: critical -> contain by: isolate the host
valid order? True
```

## Check yourself

1. The indicators are a port scan and a stolen password. What is the
   severity?
   *High: the worst indicator decides.*
2. Why isolate a host rather than switch it off?
   *Its memory and logs stay available as evidence.*
3. Why contain before eradicating?
   *Otherwise the attack spreads while you are cleaning.*
4. What goes wrong if you recover before eradicating?
   *You restore the attacker's access and are reinfected.*
5. Is `["identify", "recover", "contain"]` a valid order?
   *No: contain must come before recover.*
