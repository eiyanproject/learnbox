---
title: "Capstone: reconstructing the timeline"
summary: Pull events from several sources into one ordered story, and read the shape of the whole intrusion from it.
order: 6
files: [timeline.py]
run: python timeline.py
hints:
  - "Each event is `(timestamp, source, description)` with an ISO-8601 timestamp string. ISO timestamps sort correctly as plain strings, but parse them with `datetime.fromisoformat` for the time arithmetic."
  - "`merge`: combine the lists from every source and sort by timestamp."
  - "`sequence`: the descriptions in time order."
  - "`dwell_time`: the seconds between the first and last event - how long the intruder was in before being caught."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **intrusion** | an attacker getting into, and acting inside, systems they should not be in |
| **source** (log source) | one system's own record: the firewall's log, the SSH server's log, a file server's log |
| **event** | one thing that happened, with a time, where it was seen, and a description |
| **timeline** | events from every source merged into one list in time order |
| **timeline reconstruction** | building that list to work out what happened |
| **ISO 8601** | the date format `2026-01-02T03:05:00`: year, month, day, `T`, hours, minutes, seconds |
| **time zone** | logs must be compared in the same zone; investigators usually convert everything to UTC |
| **UTC** | Coordinated Universal Time, the shared reference clock |
| **privilege use** | the intruder using rights beyond an ordinary user's, such as `sudo` |
| **exfiltration** | copying data out of the organisation |
| **dwell time** | from the first malicious event to the last: how long the intruder went unnoticed |
| **incident report** | the written account of what happened, when, and how |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `journalctl --since "2026-01-02 03:00" --until "2026-01-02 04:00"` | one machine's log for a time window |
| `sort file` | sorts lines; ISO timestamps at the start of each line sort into time order |
| `python timeline.py` | runs your program: merges three sources and prints the dwell time |

### Python names

| Name | What it does |
|---|---|
| `(timestamp, source, description)` | one event, as a tuple |
| `[e for source in sources for e in source]` | every event from every list, in one flat list |
| `sorted(events, key=lambda e: e[0])` | the events sorted by their first item, the timestamp |
| `lambda e: e[0]` | a tiny unnamed function: "given an event, give its timestamp" |
| `for _, _, desc in ...` | takes each event apart, keeping only the description |
| `from datetime import datetime` | loads the date-and-time type |
| `datetime.fromisoformat(s)` | an ISO 8601 string turned into a date and time |
| `(last - first).total_seconds()` | the gap between two times, in seconds |
| `int(x)` | a whole number |

---

An intrusion touches many systems, and each keeps its own log. The firewall
saw the scan. The SSH server saw the login. The file server saw the files
being read. The proxy saw the upload. No single log tells the story.
**Timeline reconstruction** merges them into one sequence in time order, and
that sequence **is** the incident report.

This capstone brings the section together. The events here are exactly what
earlier lessons detected: a port scan (Network lesson 3), a brute-force
success (Forensics lesson 1), a file access, a transfer out. Now they become
the account an investigator hands over.

## Merging the sources

Each event is a `(timestamp, source, description)` tuple, with an **ISO 8601**
timestamp such as `2026-01-02T03:05:00`. This format has a useful property:
its fields go from biggest to smallest (year, month, day, hour, minute,
second), so sorting the strings alphabetically also sorts them by time.

```text
fw     2026-01-02T03:00:00  port scan from 10.0.0.9
sshd   2026-01-02T03:05:00  brute-force login succeeded
nfs    2026-01-02T03:20:00  bulk file access
```

Put every source's events in one list, sort by timestamp, and the story reads
from top to bottom.

One real-world catch: every source must use the same **time zone** and a
correct clock. Investigators convert everything to **UTC** before merging,
because a log written in local time can put an event an hour out of order.

## The shape of an intrusion

In order, the events usually tell a familiar story:

```text
scan  ->  brute-force login  ->  privilege use  ->  data access  ->  exfiltration
```

1. **Scan**: find out what is running.
2. **Login**: get in, here by guessing a password.
3. **Privilege use**: gain more rights, for example with `sudo`.
4. **Data access**: find and read what is valuable.
5. **Exfiltration**: copy it out.

Reading that shape is the skill. It also tells you where each defence could
have stopped the attack: a firewall rule at step 1, a strong password or a
lockout at step 2, and so on.

## Dwell time

The **dwell time** is the time from the first malicious event to the last. It
is the number every incident report leads with, because it measures how long
the intruder worked without being noticed. Python's `datetime` does the
arithmetic:

```pycon
>>> from datetime import datetime
>>> first = datetime.fromisoformat("2026-01-02T03:00:00")
>>> last = datetime.fromisoformat("2026-01-02T03:20:00")
>>> int((last - first).total_seconds())
1200
```

Twenty minutes here. In real incidents, dwell times are often counted in days
or weeks.

## Your turn

In `timeline.py` (events are `(timestamp, source, description)`, and
timestamps are ISO 8601 strings):

- `merge(sources)`: all the events from a list of event lists, sorted by time.
- `sequence(sources)`: just the descriptions, in time order.
- `dwell_time(sources)`: the seconds between the earliest and the latest event
  (`0` when there are fewer than two events).

Run it:

```text
['port scan from 10.0.0.9', 'brute-force login succeeded', 'bulk file access']
dwell seconds: 1200
```

## Check yourself

1. Why is no single log enough to tell the story of an intrusion?
   *Each system saw only its own part.*
2. Why do ISO 8601 timestamps sort correctly as plain strings?
   *Their fields go from the largest unit to the smallest.*
3. Why convert every log to UTC before merging?
   *Different time zones would put events out of order.*
4. What is dwell time?
   *The time from the first malicious event to the last.*
5. What usually comes between the login and the data access?
   *Privilege use: gaining more rights.*
