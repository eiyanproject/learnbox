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
