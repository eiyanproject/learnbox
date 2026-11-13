---
title: "Challenge: work the whole intrusion"
summary: The capstone of the track - raw logs and indicators in, a complete incident verdict out.
order: 6
files: [verdict.py]
run: python verdict.py
hints:
  - "Compromised ip: parse the auth log, find the ip with more than five FAILED attempts that is then followed by an OK - the brute force that worked."
  - "Severity is the worst indicator (data_exfiltration is critical); containment follows from severity; dwell is the seconds between the first and last auth-log timestamp."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **intrusion** | an attacker getting into and acting inside a system |
| **verdict** | the summary an analyst hands over: who, how serious, what to do, how long |
| **authentication log** | the record of login attempts (Forensics lesson 1) |
| **brute force that worked** | many failed logins from one address, then a success from the same address |
| **compromised IP** | the address the attacker logged in from |
| **indicator** | a sign of attack, such as `data_exfiltration` or `port_scan` |
| **severity** | how serious the incident is, set by the worst indicator (Defence lesson 6) |
| **containment** | the immediate action: isolate the host, disable the account, or monitor |
| **dwell time** | the seconds from the first log entry to the last (Forensics lesson 6) |
| **ISO 8601 timestamp** | a time written `2026-01-02T03:04:05` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python verdict.py` | runs your program: prints the verdict dict |

### Python names

| Name | What it does |
|---|---|
| `AUTH_LOG`, `INDICATORS` | given to you in `data.py`: the log lines and the indicator names |
| `line.split()` | a log line cut into words |
| `p.startswith("ip=")`, `p[3:]` | finds the `ip=` field; the address without its prefix |
| `failures.get(ip, 0) + 1` | counts failures per address |
| `datetime.fromisoformat(ts)` | a timestamp string turned into a time |
| `max(times) - min(times)` | the span from the earliest to the latest |
| `.total_seconds()` | that span in seconds |
| `{"compromised_ip": ..., "severity": ..., ...}` | the verdict, as a dict |

---

Everything the security track has built comes together here. You are given
the raw output of an intrusion, an authentication log and a list of
indicators, and must produce the **verdict** an analyst hands over:

- **who** got in;
- **how serious** it is;
- **what to do first**;
- **how long** the attacker was inside.

## The brief

`AUTH_LOG` (lines of the form `TS sshd RESULT user=U ip=IP`) and `INDICATORS`
(a list of indicator names) are in `data.py`. Produce a verdict dict with
four keys:

| Key | Value | From |
|---|---|---|
| `compromised_ip` | the address with **more than five** failed logins, followed by a success from the same address; `None` if there is none | Forensics lesson 1 |
| `severity` | the worst of the indicators: `data_exfiltration` and `ransomware` are `critical`, `credential_compromise` is `high`, `port_scan` is `low` | Defence lesson 6 |
| `containment` | `isolate the host` for critical, `disable the affected account` for high, otherwise `monitor` | Defence lesson 6 |
| `dwell_seconds` | the seconds between the first and the last auth-log entry | Forensics lesson 6 |

Each part is a lesson you have already done; the challenge is putting them
together into one answer.

## Your turn

In `verdict.py`, write `investigate(auth_log, indicators)`, returning the
verdict dict.

## Check yourself

1. Five failures and then a success from one address. Is it compromised by
   this rule?
   *No: it needs more than five.*
2. The indicators are `port_scan` and `credential_compromise`. What is the
   containment?
   *Disable the affected account: the severity is high.*
3. How is dwell time measured here?
   *From the first auth-log timestamp to the last.*
