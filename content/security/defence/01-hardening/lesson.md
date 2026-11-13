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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **hardening** | changing a system's settings to remove ways in |
| **default** | the setting a program ships with, before anyone changes it |
| **configuration** (config) | the file of settings that controls how a program behaves |
| **setting** (option) | one named value in a config, such as `PermitRootLogin yes` |
| **insecure value** | a setting known to be dangerous |
| **secure value** | the setting to use instead |
| **finding** | one problem a review discovered |
| **remediation** | fixing the findings |
| **benchmark** | a published list of recommended settings, such as the CIS Benchmarks or the DISA STIGs |
| **CIS** | the Center for Internet Security, which publishes benchmarks for many systems |
| **OpenSCAP** | a tool that checks a machine against a benchmark automatically |
| **SSH** | the protocol and service for logging in to a machine remotely |
| **`sshd_config`** | the SSH server's configuration file, `/etc/ssh/sshd_config` |
| **`PermitRootLogin`** | whether the all-powerful `root` account may log in over SSH |
| **`PasswordAuthentication`** | whether SSH accepts passwords; `no` means keys only |
| **key-based login** | logging in with a key pair instead of a password; cannot be guessed |
| **`X11Forwarding`** | lets remote graphical programs reach your screen; rarely needed on a server |
| **`Protocol 1`** | the broken first version of SSH, removed from OpenSSH in 2017 |
| **debug mode** | an application setting that shows internal details; never for production |
| **production** | the real, live system that users rely on |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sudo sshd -T` | prints the SSH server's effective settings, after all defaults and files |
| `sudo sshd -t` | checks the config file for errors without restarting |
| `grep -i permitrootlogin /etc/ssh/sshd_config` | finds one setting in the file |
| `python harden.py` | runs your program: lists the findings and prints the hardened config |

### Python names

| Name | What it does |
|---|---|
| `RULES` | given to you: a dict from setting name to `(insecure, secure)` |
| `for name, (bad, _good) in RULES.items()` | each rule, taken apart into its name and its two values |
| `config.get(name) == bad` | the config holds the insecure value (a missing setting gives `None`) |
| `sorted(...)` | the names in alphabetical order |
| `dict(config)` | a copy of the dict, so the original is not changed |
| `RULES[name][1]` | the secure value |
| `findings(config) == []` | there is nothing left to fix |

---

Attackers rarely need a clever exploit when a **default** was left in place.
Remote login as `root` enabled, password login on a server that should only
accept keys, a debug mode showing internal details, a service listening on
every network interface: each is a door left open by a setting nobody
changed. **Hardening** is the unglamorous, valuable work of closing them.

## Review against known-bad settings

Hardening is systematic, not creative. You compare a **configuration** with
a list of settings known to be dangerous, and for each one that matches, you
set the safe value instead. Examples from an SSH server's `sshd_config`, plus
one from an application's own config:

| Setting | Insecure | Secure | Why |
|---|---|---|---|
| `PermitRootLogin` | `yes` | `no` | `root` can do anything; log in as yourself and use `sudo` |
| `PasswordAuthentication` | `yes` | `no` | passwords can be guessed (Forensics lesson 1); keys cannot |
| `X11Forwarding` | `yes` | `no` | a feature a server rarely needs is extra attack surface |
| `Protocol` | `1` | `2` | SSH version 1 is broken |
| `debug` *(application)* | `true` | `false` | debug pages show internals to anyone |

Two notes on that list:

- `Protocol 1` meant the broken first version of SSH. OpenSSH removed it
  entirely in version 7.6 (2017), so on a current system the line does
  nothing. But finding it is a strong sign that the config, and maybe the
  whole server, has not been reviewed in years.
- `debug` is not an SSH setting. It stands for the debug mode of a web
  application or framework, which in **production** shows error traces,
  internal file paths, and sometimes even an interactive console.

`sudo sshd -T` prints the settings an SSH server is really using, after
defaults and every config file are combined. That is the list to check, not
just the file.

## Benchmarks

You do not invent the list yourself. **Benchmarks** such as the CIS
Benchmarks and the DISA STIGs list hundreds of settings for each kind of
system, each with a recommended value. The Practical Linux Hardening Guide
reports that following CIS removes most known vulnerabilities, and recommends
checking automatically with a tool such as **OpenSCAP** rather than by hand.
It also gives a short list of general rules:

- never use the `root` account for anything that does not need it;
- use `sudo` for single commands;
- make services give up their extra privileges once they have started;
- allow only the network access that is needed (Network lesson 6);
- do not install software you do not need.

Building the check for a handful of settings is building the whole idea.

## The defender's habit

Find the settings at fault, report them as **findings**, and produce the
corrected configuration: review and **remediation** in one pass. Working from
a fixed list makes it repeatable, and means nothing is forgotten. That is the
point: a missed setting is a door you never notice is open, until someone
walks through it.

## Your turn

`RULES` (setting to `(insecure, secure)`) is given to you. In `harden.py`:

- `findings(config)`: the sorted setting names whose value is the insecure
  one.
- `harden(config)`: a copy of the config with every finding corrected. Do not
  change the original.
- `is_hardened(config)`: `True` when there is nothing left to fix.

Run it:

```text
findings: ['PermitRootLogin', 'debug']
hardened: {'PermitRootLogin': 'no', 'Protocol': 2, 'debug': False}
```

## Check yourself

1. Why turn off `PermitRootLogin`?
   *`root` can do anything; people should log in as themselves and use
   `sudo`.*
2. What does `PasswordAuthentication no` force?
   *Key-based login, which cannot be guessed.*
3. You find `Protocol 1` in a modern server's config. What does it tell you?
   *The setting does nothing now, but the config has not been reviewed in
   years.*
4. Why check `sshd -T` and not just the file?
   *It shows the settings actually in effect, defaults included.*
5. Why should `harden` return a copy?
   *So the original config is left as it was.*
