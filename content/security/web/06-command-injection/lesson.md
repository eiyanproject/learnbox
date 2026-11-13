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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **shell** | the program that reads a command line, splits it up and runs it: `bash`, `sh` |
| **command string** | a whole command line as one piece of text, for a shell to interpret |
| **argument** | one word given to a program: in `echo pinging host`, `pinging` and `host` |
| **metacharacter** | a character with a special meaning to the shell: `;` `\|` `&` `$` `` ` `` `>` `<` |
| **`;`** | ends one command and starts the next |
| **`\|`**, **`&&`** | pass output to the next command; run the next command only if this one succeeded |
| **`$( )`**, backticks | run a command and put its output here |
| **command injection** | user input that adds commands to a shell command line |
| **privileges** | what an account may do; the injected command runs with the server's |
| **argument list** | the program and its arguments as separate items, run with no shell in between |
| **literal** | taken exactly as written, with no special meaning |
| **argument injection** | input starting with `-` that a program reads as an option; `--` ends the options |
| **allow-list validation** | accept only input of a known good form, such as a valid host name |
| **defence in depth** | several layers of protection, so one failure is not the end |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `echo pinging host` | prints `pinging host`; the lesson's stand-in for a real tool such as `ping` |
| `expr 6 \* 7` | prints `42`; the `\` stops the shell treating `*` as "every file" |
| `a ; b` | runs `a`, then `b` |
| `python shellcmd.py` | runs your program: the payload through the vulnerable and the safe function |

### Python names

| Name | What it does |
|---|---|
| `os.popen(cmd).read()` | runs `cmd` **through a shell** and returns what it printed |
| `import subprocess` | loads the module for running programs |
| `subprocess.run([...], capture_output=True, text=True)` | runs the program in the list directly, with no shell, and captures its output as text |
| `.stdout` | what that program printed |
| `r"..."` | a raw string: backslashes are kept as they are |
| `print(x, end="")` | prints without adding another newline |
| `.strip()` | removes spaces and newlines at both ends |
| `run_vulnerable(host)` | given to you: runs `"echo pinging " + host` through a shell |

---

Some features need to run another program: ping a host, convert an image,
look something up with a command-line tool. When the user's input is pasted
into a command line that a **shell** will read, the shell's own syntax
becomes available to the attacker, and the shell runs whatever they add.

## What the shell does with a command string

A shell reads a line of text and splits it up using its
**metacharacters**: characters with special meanings. A few of them:

| Characters | Meaning to the shell |
|---|---|
| `;` | end this command, start the next |
| `\|` | send this command's output into the next |
| `&&` | run the next command if this one worked |
| `$( )` or backticks | run a command and paste in its output |

Those meanings apply wherever the characters appear in the string, including
inside the part that came from a user.

## The attack

The vulnerable code builds one string and gives it to a shell:

```python
os.popen("echo pinging " + host).read()
```

(The lesson uses `echo` as a harmless stand-in for a real tool like `ping`.)
With the host `127.0.0.1`, the shell runs `echo pinging 127.0.0.1`. Fine.

Now send this as the host:

```text
127.0.0.1; expr 6 \* 7
```

The shell sees the `;` and runs **two** commands: the intended `echo`, then
`expr 6 * 7`, which prints `42`. The `42` is nowhere in the input, so seeing
it proves the injected command ran. A real attacker's second command would
not do arithmetic: it would read files or change data, with all the
**privileges** of the server's account. You will write that payload.

## The defence: no shell at all

The fix is **not** to escape the metacharacters. Each shell has its own
quoting rules, and getting every case right is a losing game. The fix is to
**not use a shell**.

Give the program and its arguments as a **list**. The operating system then
runs exactly that program with exactly those arguments, and nothing ever
splits the string:

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

In the second version, the whole of `127.0.0.1; expr 6 \* 7` is **one
argument** to `echo`: literal text, printed and never run. There is no command
boundary for `;` to make, because there is no shell to read it.

OWASP's OS Command Injection Defense Cheat Sheet adds more layers on top:

- **Validate** the input against an **allow-list**, such as "a valid host
  name or IP address", and refuse everything else. This is good **defence in
  depth**, but removing the shell is the fix that actually closes the hole.
- Watch for **argument injection**: even with no shell, an input such as
  `-o /tmp/x` may be read by the program as an option. Putting `--` before
  user values tells most programs "no more options after this".
- Better still, if a library can do the job (Python's `socket` module instead
  of calling `ping`), use it and run no program at all.

The same rule has now appeared four times: SQL, HTML, file paths, and the
shell. Keep untrusted input as data; never let it become code.

## Your turn

`run_vulnerable(host)` is given to you. In `shellcmd.py`:

- `injection_payload()`: a `host` value that makes a second command run
  through `run_vulnerable`, so that its output contains `42`. The payload
  itself must not contain `42`: the injected command has to **compute** it.
- `run_safe(host)`: run the same `echo pinging <host>` without a shell, as an
  argument list, and return its output. The payload is then one literal
  argument and `42` never appears.

Run it:

```text
vulnerable: pinging 127.0.0.1
42
safe:       pinging 127.0.0.1; expr 6 \* 7
```

## Check yourself

1. What does `;` mean to the shell?
   *End this command and start another.*
2. How does the lesson's payload prove that the injected command ran?
   *Its output, `42`, is computed and does not appear in the input.*
3. Why does the list form of `subprocess.run` stop the attack?
   *No shell reads the string, so the input is one literal argument.*
4. Why not escape the metacharacters instead?
   *Quoting rules differ between shells, and it is easy to miss a case.*
5. Is validating the host name enough on its own?
   *It helps, but removing the shell is the real fix.*
