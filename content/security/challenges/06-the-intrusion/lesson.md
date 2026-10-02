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

Everything the track has built comes together here. You are handed the raw
output of an intrusion - an authentication log and a list of indicators - and
must produce the verdict an analyst hands over: who got in, how serious it is,
what to do first, and how long they were inside.

## The brief

`AUTH_LOG` (lines of `TS sshd RESULT user=U ip=IP`) and `INDICATORS` (a list of
indicator names) are in `data.py`. Produce a verdict dict:

- `compromised_ip` - the ip with more than five failed logins followed by a
  success
- `severity` - the worst of the indicators (`data_exfiltration` and `ransomware`
  are `critical`, `credential_compromise` `high`, `port_scan` `low`)
- `containment` - `isolate the host` for critical, `disable the affected account`
  for high, else `monitor`
- `dwell_seconds` - seconds between the first and last auth-log entry

This is the log analysis, timeline, and incident-response lessons in one answer.

## Your turn

In `verdict.py`, write `investigate(auth_log, indicators)` returning the verdict
dict.
