---
title: Command injection
summary: A feature that hands user input to a shell, an extra command smuggled in, and the fix that is to stop using a shell at all.
order: 6
files: [shellcmd.py]
run: python shellcmd.py
hints:
  - "`injection_payload`: a value that looks like a host but ends the first command and starts a second, e.g. `127.0.0.1; expr 6 \\* 7`. The `;` separates shell commands."
  - "`run_vulnerable` is provided and runs `echo pinging <host>` through a shell, so your second command runs too - its output (42) appears though it is nowhere in the input."
  - "`run_safe`: do not build a shell string. Use `subprocess.run([\"echo\", \"pinging\", host], capture_output=True, text=True).stdout` - a list, with no shell to interpret the metacharacters."
  - "With the list form there is no shell, so `; expr 6 * 7` is just literal text passed to echo, never a command."
---

Some features need to run a program: ping a host, convert an image, look up a
record with a command-line tool. When the user's input is pasted into a
**shell** command string, the shell's own syntax becomes available to the
attacker - and the shell will happily run whatever they add.

## The attack

```python
os.popen("echo pinging " + host).read()
```

The shell sees one string and splits it on *its* metacharacters. A `host` of
`127.0.0.1; expr 6 \* 7` becomes two commands: the intended `echo`, then
`expr 6 * 7`. The second runs with the server's privileges. Here it harmlessly
computes `42` - proof the injection executed, since `42` is nowhere in the input
- but in the real world that second command reads files, opens a reverse shell,
or deletes data. `;`, `|`, `&&`, backticks and `$()` are all doorways. You will
write the payload that smuggles the second command in.

## The defence

The fix is not to escape shell metacharacters - that is a losing game across
shells and quoting rules. The fix is to **not use a shell**. Pass the program
and its arguments as a **list**, so the operating system runs exactly that
program with exactly those arguments and no shell ever parses the string:

```python
subprocess.run(["echo", "pinging", host], capture_output=True, text=True)
```

Both versions side by side, with the same input:

```pycon
>>> import os, subprocess
>>> host = r"127.0.0.1; expr 6 \* 7"
>>> print(os.popen("echo pinging " + host).read(), end="")    # through a shell
pinging 127.0.0.1
42
>>> result = subprocess.run(["echo", "pinging", host], capture_output=True, text=True)
>>> print(result.stdout, end="")                               # no shell
pinging 127.0.0.1; expr 6 \* 7
```

Now `127.0.0.1; expr 6 \* 7` is a single argument to `echo` - literal text,
printed and never executed. There is no command boundary for `;` to create,
because there is no shell to find it. (Validating the input against an allow-list
of valid hostnames is worthwhile defence-in-depth, but removing the shell is the
fix that actually closes the hole.)

The same principle has now appeared four times: SQL, HTML, file paths, shell.
Keep untrusted input as data; never let it become code.

## Your turn

`run_vulnerable(host)` is provided. In `shellcmd.py`:

- `injection_payload()` - a `host` value that makes a second command run through
  `run_vulnerable`, whose output contains `42`. The payload itself must not
  contain `42` - have the injected command *compute* it
- `run_safe(host)` - run the same `echo pinging <host>` without a shell, as an
  argument list, and return its output; the payload is then one literal
  argument and `42` never appears
