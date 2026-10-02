---
title: Hardening a configuration
summary: Most breaches start with a default left insecure. Reviewing a config against known-bad settings, and fixing them, is the cheapest defence there is.
order: 1
files: [harden.py]
run: python harden.py
hints:
  - "`RULES` maps each setting to `(insecure_value, secure_value)`. A config is at fault for a setting when its value equals the insecure one."
  - "`findings`: return the sorted list of setting names whose value matches the insecure value in RULES."
  - "`harden`: copy the config and set every at-fault setting to its secure value."
  - "`is_hardened`: there are no findings left."
---

Attackers rarely need a clever exploit when a **default** was left in place.
Remote root login enabled, password authentication on a server that should use
keys, debug mode exposing internals, a service listening on every interface -
each is a door left open by a setting nobody changed. Hardening is the
unglamorous, high-value work of closing them.

## Review against known-bad

Hardening is systematic, not creative: you compare a configuration against a
list of settings known to be dangerous, and for each one that matches, you set
it to its safe value. The canonical examples for an SSH server:

| Setting | Insecure | Secure |
|---|---|---|
| `PermitRootLogin` | `yes` | `no` |
| `PasswordAuthentication` | `yes` | `no` (keys only) |
| `X11Forwarding` | `yes` | `no` |
| `Protocol` | `1` | `2` |
| `debug` | `true` | `false` |

Benchmarks like the CIS guides are exactly this, at scale: hundreds of
settings, each with a known-good value, checked automatically. Building the
check for a handful is building the whole idea.

## The defender's habit

Find the at-fault settings, report them, and produce the corrected
configuration - review and remediation in one pass. Doing it from a fixed list
means it is repeatable and cannot be forgotten, which is the point: a mistake
here is a door you never notice is open until someone walks through it.

## Your turn

`RULES` (setting to `(insecure, secure)`) is provided. In `harden.py`:

- `findings(config)` - the sorted setting names whose value is the insecure one
- `harden(config)` - a copy of the config with every at-fault setting corrected
- `is_hardened(config)` - `True` when nothing is left to fix
