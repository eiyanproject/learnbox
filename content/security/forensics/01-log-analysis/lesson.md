---
title: Reading the logs
summary: An attack leaves a trail in the logs; forensics starts with parsing that trail and seeing the brute-force attempt in it.
order: 1
files: [logs.py]
run: python logs.py
hints:
  - "`parse_line`: the fields are space-separated `key=value` after a timestamp, service and result. Split into parts and pull out `user=` and `ip=`."
  - "A line that does not have the expected shape should return `None`, not crash - real logs have junk in them."
  - "`failed_by_ip`: count only the lines whose result is `FAILED`, grouped by ip."
  - "`compromised_ips`: an ip with more than `threshold` failures that is then followed by an `OK` from the same ip - a brute force that eventually worked."
---

Every incident investigation begins the same way: with the **logs**. An attacker
who tried to break in left failed-login records; one who succeeded left a
success among them. The skill is turning thousands of lines into the handful
that tell the story.

## The shape of a log

Authentication logs are lines of fields. A simplified form:

```text
2026-01-02T03:04:05 sshd FAILED user=admin ip=10.0.0.9
2026-01-02T03:04:49 sshd OK user=admin ip=10.0.0.9
```

Parsing is the whole game, and it must be **robust**: real logs contain blank
lines, truncated entries and formats you did not expect, and a parser that
crashes on the first odd line is useless. Unparseable lines are skipped, not
fatal.

## The brute-force signature

A brute force is many failures from one source in a short time. On its own that
is just noise an attacker generates constantly. What matters - the thing that
turns an alert into an incident - is a burst of failures from an ip **followed
by a success** from that same ip. That is a guess that landed: an account
compromised. Finding those is the exercise.

## Your turn

In `logs.py`:

- `parse_line(line)` - `{ts, service, result, user, ip}` (`user` and `ip`
  without their `user=` / `ip=` prefixes), or `None` if the line does not have
  that shape or its result is anything other than `FAILED` or `OK`
- `failed_by_ip(lines)` - a dict of ip to number of `FAILED` attempts
- `compromised_ips(lines, threshold=5)` - the set of ips with more than
  `threshold` failures that are then followed by an `OK` from the same ip
