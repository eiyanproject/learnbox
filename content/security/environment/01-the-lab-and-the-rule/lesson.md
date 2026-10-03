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

This track teaches how attacks work so you can stop them. That knowledge is
ordinary and useful - it is what every defender, tester and incident responder
relies on - and it comes with one rule.

## The rule

**Everything you do here stays inside this container.** Every target you attack
in these lessons is a program that lives in this box, on `localhost`, put there
for you to practise on. You never point a tool at a machine you do not own and
have permission to test. Not the network this container sits on, not the
Proxmox host, not a server on the internet. That is the line between security
work and a crime, and it is drawn by *permission*, not by technique - the same
`nmap` command is routine on your own lab and, aimed at someone else's network
without permission, can break computer-misuse laws in many countries.

Keep that rule and everything in this track is something you can be proud to
know. The skills are the same ones a defender uses to find the hole before an
attacker does.

## How a lesson works

Each lesson is the explanation on the left and a real shell and editor on the
right, the same as every other track. The difference is what you are building:
a script that attacks a local target, a fix that closes a hole, or an answer
you have recovered from a file.

- **Run** types the lesson's command into the terminal.
- **Check** runs hidden tests and shows which pass.
- **Reset** restores the starter files.

## A warm-up

Security work drowns in **encodings** - text wrapped in a reversible format so
it survives being copied around. Base64 is the most common. It looks like
scrambled nonsense and protects nothing: anyone can reverse it. Recognising it,
and reversing it, is a reflex you will use constantly.

```python
import base64
base64.b64encode(b"hello")      # b'aGVsbG8='
base64.b64decode(b"aGVsbG8=")   # b'hello'
```

## Your turn

In `warmup.py`, finish `reveal(encoded)` so it takes a base64 string and
returns the original text. Press **Check** to confirm the grader works.
