---
title: "Round 1: Who is knocking?"
summary: Read an authentication log and name the addresses that are guessing passwords.
order: 1
files: [knock.py]
run: python -i knock.py
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 300
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **authentication log** (auth log) | the record of every login attempt, one per line |
| **on-call** | the person who answers alerts out of hours |
| **suspect** | an address that looks like it is guessing passwords |
| **block** | stop an address reaching the service, for example with a firewall rule |
| **threshold** | how many failures count as an attack: here 5 |
| **window** | how close together in time they must be: here 60 seconds |
| **run of failures** | several failures from the same address, taken in time order |
| **sliding window** | checking every group of `threshold` consecutive failures, not only the first |
| **junk line** | a line that does not have the expected shape; skip it |
| **ISO 8601 timestamp** | a time written `2026-03-04T10:00:07` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i knock.py` | runs your file, then leaves Python open so you can call `suspects(...)` yourself |

### Python names

| Name | What it does |
|---|---|
| `line.split()` | the line cut into words |
| `p.startswith("ip=")`, `p[3:]` | finds the `ip=` field; the address without its prefix |
| `datetime.fromisoformat(ts)` | a timestamp string turned into a time you can subtract |
| `(later - earlier).total_seconds()` | the gap between two times, in seconds |
| `times[i + threshold - 1]` | the last failure in a run of `threshold` starting at `i` |
| `d.setdefault(ip, []).append(t)` | collects each address's failure times in a list |
| `sorted(set_of_ips)` | the addresses as a sorted list |

---

The on-call phone went off: login failures are up. You have the auth log and
twelve minutes to say who to block.

## The log

One event per line, oldest first:

```text
2026-03-04T10:00:07 FAILED user=root ip=203.0.113.9
2026-03-04T10:00:09 OK user=ana ip=198.51.100.4
```

A timestamp, then `FAILED` or `OK`, then `user=` and `ip=`. Real logs have
junk in them: skip any line that does not have this shape.

## The task

In `knock.py`, write `suspects(lines, threshold=5, window=60)`.

Return a **sorted list** of the IP addresses that had at least `threshold`
failed logins within `window` seconds of each other - that is, some run of
`threshold` failures from that address whose first and last are no more than
`window` seconds apart.

- Only `FAILED` lines count. A successful login in between does not reset
  anything.
- Failures are counted per address, whatever the user name.
- An address that fails slowly - five times over an hour - is not a suspect.

```text
five failures from 203.0.113.9 between 10:00:07 and 10:00:40   ->  suspect
five failures from 198.51.100.4, ten minutes apart             ->  not one
```

`datetime.fromisoformat` reads these timestamps.
