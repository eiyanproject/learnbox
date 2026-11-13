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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **forensics** | working out what happened on a system, after the fact, from the traces it left |
| **incident** | a security event that matters: a real break-in, not just an attempt |
| **log** | a file (or journal) where a program writes a line for each thing that happens |
| **log line** (entry) | one event: a time, the program, what happened, and details |
| **timestamp** | the date and time of an event, here in ISO 8601 form `2026-01-02T03:04:05` |
| **service** | the program that wrote the line, such as `sshd` (the SSH server) |
| **field** | one piece of a log line |
| **`key=value`** | a field that names itself, such as `user=admin` |
| **parse** | turn a line of text into named fields a program can use |
| **robust parser** | one that skips lines it cannot understand instead of crashing |
| **authentication log** | the record of login attempts, failed and successful |
| **brute force** | trying password after password until one works |
| **signature** | the pattern that identifies an activity |
| **threshold** | how many failures count as "many" |
| **compromised account** | one the attacker got into |
| **noise** | the constant background of failed attempts from automated scanners |
| **alert** | a notice that something may be wrong; an incident is when it really is |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `journalctl -u sshd` | shows the SSH server's log on a systemd machine |
| `grep 'Failed password' /var/log/auth.log` | the failed SSH logins, on systems that keep a text log |
| `grep ... \| awk '{print $11}' \| sort \| uniq -c \| sort -nr` | count lines per address, most frequent first (the column number depends on the format) |
| `python logs.py` | runs your program: counts failures and finds the compromised address |

### Python names

| Name | What it does |
|---|---|
| `line.split()` | the line cut into words at any whitespace |
| `len(parts) < 3` | fewer than three words: not a log line of this shape |
| `p.startswith("user=")` | `True` when the word begins with `user=` |
| `p[5:]` | the word without its first five characters (`user=`) |
| `rec["result"] not in ("FAILED", "OK")` | the result is something else |
| `counts.get(ip, 0) + 1` | the count so far (0 if none), plus one |
| `if rec and rec["ip"]:` | the line parsed, and it has an address |
| `continue` | skip to the next line |
| `f"{i:02d}"` | a number as two digits, `07` |

---

Every incident investigation begins the same way: with the **logs**. An
attacker who tried to break in left a record of failed logins. One who got in
left a success among them. The skill is turning thousands of lines into the
handful that tell the story.

The Trail of Bits CTF guide makes a point worth keeping in mind for this whole
section: real **forensics** is mostly not clever puzzles. It is knowing where
the traces are (logs, file metadata, timestamps) and reading them carefully.

## What a log line looks like

Authentication logs are lines of **fields**. A simplified form, as used in
this lesson:

```text
2026-01-02T03:04:05 sshd FAILED user=admin ip=10.0.0.9
2026-01-02T03:04:49 sshd OK user=admin ip=10.0.0.9
```

From left to right: the **timestamp**, the **service** that wrote it (`sshd`,
the SSH server), the result, and two **`key=value`** fields saying which
account and which address.

A real SSH server's log carries the same facts in a wordier form, such as
`Failed password for admin from 10.0.0.9 port 52344 ssh2`, read with
`journalctl -u sshd` or from `/var/log/auth.log`.

## Parse robustly

Parsing, turning each line into named fields, is most of the work:

```pycon
>>> from logs import parse_line
>>> parse_line("2026-01-02T03:04:05 sshd FAILED user=admin ip=10.0.0.9")
{'ts': '2026-01-02T03:04:05', 'service': 'sshd', 'result': 'FAILED', 'user': 'admin', 'ip': '10.0.0.9'}
>>> print(parse_line("garbage"))
None
```

The parser must be **robust**. Real logs contain blank lines, cut-off entries,
and messages in formats you did not expect. A parser that crashes on the first
odd line is useless in an investigation, so a line that does not fit returns
`None` and is skipped.

## The brute-force signature

A **brute force** is many failed logins from one address in a short time. On
its own, that is mostly **noise**: automated scanners try common passwords
against every SSH server on the internet, all day long.

What turns an alert into an **incident** is a burst of failures from an
address **followed by a success from the same address**. That is a guess that
worked: a **compromised account**.

```text
03:04:00  FAILED  admin  10.0.0.9
03:04:01  FAILED  admin  10.0.0.9
...       (8 failures in all)
03:05:00  OK      admin  10.0.0.9     <- the attacker is in
```

Finding those addresses is the exercise. The order matters: count failures as
you go, and when an `OK` arrives, check how many failures that address already
had.

## Your turn

In `logs.py`:

- `parse_line(line)`: a dict `{ts, service, result, user, ip}`, with `user` and
  `ip` given without their `user=` and `ip=` prefixes. Return `None` if the
  line does not have that shape, or if its result is anything other than
  `FAILED` or `OK`.
- `failed_by_ip(lines)`: a dict from each address to its number of `FAILED`
  attempts.
- `compromised_ips(lines, threshold=5)`: the set of addresses with **more
  than** `threshold` failures that are then followed by an `OK` from the same
  address.

Run it:

```text
failed: {'10.0.0.9': 8}
compromised: {'10.0.0.9'}
```

## Check yourself

1. Why must a log parser skip lines it cannot read rather than crash?
   *Real logs contain junk, and one odd line must not stop the
   investigation.*
2. Many failed logins from one address. Incident or noise?
   *Usually noise, until a success follows.*
3. What is the sign of a brute force that worked?
   *Many failures, then an `OK` from the same address.*
4. An address has 3 failures, then an `OK`, with `threshold=5`. Is it
   flagged?
   *No: 3 is not more than 5. It looks like someone mistyping.*
5. Why does the order of the lines matter?
   *The success has to come after the failures.*
