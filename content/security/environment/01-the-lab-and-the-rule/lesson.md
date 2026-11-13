---
title: The lab, and the one rule
summary: What this container is, the single rule that governs every lesson, and how the Check button grades your work.
order: 1
files: [warmup.py]
run: python warmup.py
hints:
  - "`import base64` and `base64.b64decode(text)` gives you bytes; `.decode()` turns bytes into a string."
  - "The input is text, so decode the result: `return base64.b64decode(encoded).decode()`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **security track** | this course: how attacks work, so you can detect and stop them |
| **container** | an isolated mini-computer this course runs in; everything you attack lives inside it |
| **`localhost`** | the name a computer uses for itself (address `127.0.0.1`); traffic to it never leaves the machine |
| **target** | a program put in the container on purpose for you to attack |
| **authorization** (permission) | the owner's agreement that you may test a system; the line between security work and a crime |
| **computer misuse law** | laws in many countries that make unauthorized access or testing a crime |
| **Proxmox host** | the physical server this container runs on; off limits |
| **defender**, **penetration tester**, **incident responder** | people who protect systems; test them with permission; investigate after an attack |
| **encoding** | rewriting data in a reversible format so it survives being copied; it uses no secret |
| **Base64** | an encoding that writes any bytes using 64 safe characters (`A-Z`, `a-z`, `0-9`, `+`, `/`, with `=` as padding) |
| **padding** (`=`) | characters at the end of Base64 that make its length a multiple of 4 |
| **bytes** | raw data, written `b"..."` in Python; not the same type as text |
| **string** (`str`) | text in Python |
| **decode** | turn bytes into text (`.decode()`), or reverse an encoding (`b64decode`) |
| **Run**, **Check**, **Reset** | the buttons: type the run command; run the hidden tests; restore the starter files |

### Python functions

| Name | What it does |
|---|---|
| `import base64` | brings in the Base64 module |
| `base64.b64encode(data)` | bytes to Base64 bytes: `b"hello"` gives `b'aGVsbG8='` |
| `base64.b64decode(text)` | Base64 (text or bytes) back to the original bytes |
| `data.decode()` | bytes to a string (UTF-8) |
| `text.encode()` | a string to bytes |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python warmup.py` | runs the warm-up file |
| `nmap` | a port scanner (a later lesson); legal on your own lab, a crime aimed at others without permission |

---

This track teaches how attacks work, so that you can stop them. That
knowledge is ordinary and useful: it is what every **defender** (who protects
systems), **penetration tester** (who attacks them, with permission, to find
the holes first) and **incident responder** (who investigates after a break-in)
relies on. It comes with one rule.

## The rule

**Everything you do here stays inside this container.**

A **container** is an isolated small Linux system, running on a bigger
server. Every target you attack in these lessons is a program that lives in
this container, on `localhost` (the name a computer uses for itself, address
`127.0.0.1`, so the traffic never leaves the machine), put there for you to
practise on.

You never point a tool at a machine you do not own, and have permission to
test. Not the network this container sits on, not the Proxmox host it runs
on, not a server on the internet:

| Target | Allowed? |
|---|---|
| a lesson's program inside this container, on `localhost` | yes: it was put there for you |
| your own computer, or a lab you own | yes |
| a system whose owner has given you written permission to test | yes, within what they agreed |
| the network around this container, or the Proxmox host | **no** |
| any server on the internet you do not own | **no** |

The line between security work and a crime is drawn by **permission**, not
by technique. The same `nmap` command (a tool that asks a computer which
services it runs, met in the Network section) is routine on your own lab,
and aimed at someone else's network without permission can break
computer-misuse laws in many countries. Professional testers work under a
written agreement that says exactly what they may touch.

Keep that rule, and everything in this track is something you can be proud
to know. The skills are the same ones a defender uses to find the hole before
an attacker does.

## How a lesson works

Each lesson is the explanation on the left and a real shell and editor on the
right, the same as every other track. What you build is one of:

- a script that **attacks** a local target, to see how the attack works;
- a **fix** that closes the hole;
- or an **answer** you recovered from a file, such as a log or a capture.

The three buttons:

- **Run** types the lesson's command into the terminal (here
  `python warmup.py`).
- **Check** runs hidden tests against your code and shows which pass.
- **Reset** restores the starter files (your old ones are kept in
  `~/learn/.reset-backups`).

## A warm-up: encodings

Security work is full of **encodings**: data rewritten in a reversible
format so that it survives being copied around, for example inside an email,
a URL or a cookie. An encoding uses **no secret**. Anyone who recognises it
can reverse it.

**Base64** is the most common. It writes any bytes using only 64 safe
characters: the letters, the digits, `+` and `/`, with `=` at the end as
**padding** when the length needs filling out. It looks like scrambled
nonsense and protects nothing:

```pycon
>>> import base64
>>> base64.b64encode(b"hello")
b'aGVsbG8='
>>> base64.b64decode(b"aGVsbG8=")
b'hello'
>>> base64.b64decode("d2VsY29tZSB0byB0aGUgbGFi").decode()
'welcome to the lab'
```

The `b` in front of `b"hello"` means **bytes**: raw data, not text. Python
keeps the two apart: `.decode()` turns bytes into a string, and `.encode()`
turns a string into bytes. `b64decode` accepts either a string or bytes, and
always gives back bytes.

Recognising Base64 (letters and digits, maybe ending in `=`, length a
multiple of 4) and reversing it is a reflex you will use constantly: in
tokens, in cookies, in configuration files, and in malware hiding its
strings. The next section's first lesson shows why "it is encoded" never
means "it is protected".

## Your turn

In `warmup.py`, finish `reveal(encoded)`: it takes a Base64 **string** and
returns the original text as a **string**, not bytes.
`reveal("aGVsbG8=")` is `"hello"`. Press **Run** to try it, then **Check**
to see the grader work.
