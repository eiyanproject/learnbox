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

An intrusion touches many systems, each with its own log: the firewall saw the
scan, the auth log saw the login, the file server saw the access, the proxy saw
the upload. No single log tells the story. **Timeline reconstruction** merges
them into one ordered sequence, and the sequence *is* the incident report.

This capstone brings the section together: the events here are the very things
earlier lessons detected - a port scan, a brute-force success, a file access, an
exfiltration - now assembled into the narrative an investigator hands over.

## The shape of an intrusion

Ordered, the events tell a familiar story:

```text
scan  ->  brute-force login  ->  privilege use  ->  data access  ->  exfiltration
```

Reading that shape is the skill. The **dwell time** - from first malicious event
to last - is the number every incident report leads with, because it measures
how long the intruder operated undetected.

## Your turn

In `timeline.py` (events are `(timestamp, source, description)`, timestamps are
ISO-8601 strings):

- `merge(sources)` - all events from a list of event-lists, sorted by time
- `sequence(sources)` - just the descriptions, in time order
- `dwell_time(sources)` - seconds between the earliest and latest event
