# learnbox

A private learning platform for programming and security. Each lesson is an
explanation on the left and a real workspace on the right: a code editor over a
real `bash` terminal, hidden tests behind a **Check** button, and hints when you
are stuck. Everything runs in one small LXC on your own network.

- **Ten tracks**, written for this project: Python, Rust, C, C++, C#, Java,
  MATLAB, CCNA, Security and Programming mindset (see [Curriculum](#curriculum))
- **Practice**: ~130 Python and ~90 Rust exercises imported from [Exercism](https://exercism.org) (MIT)
- **Profiles**: a few people can share one box, each with their own progress
  and files - picked from a list, no login
- **Terminal**: a free scratch shell with `python`, `cargo` and `git`

Python runs from `print()` to metaclasses, asyncio, a mini ORM and a capstone
key-value store. Rust runs from `cargo run` to unsafe, a hand-written async
executor, FFI and a concurrent TCP server.

Styling follows the *Recipe Catalog Terminal* Claude Design canvas: cyan as the
one accent, magenta for passed work, amber for shortfalls, Chakra Petch and IBM
Plex Mono. Dark and light themes.

## Curriculum

### Python

**Beginner** (12) — Hello, Python; Variables and numbers; Functions; Strings; Making decisions; Loops; Lists and tuples; Dictionaries and sets; Comprehensions; Errors and exceptions; Files and data; Classes

**Intermediate** (10) — Functions in depth; Scope and closures; Decorators; Iterators and generators; The collections toolbox; Dataclasses and enums; Context managers; Modules and packages; Regular expressions; Recursion and algorithms

**Advanced** (10) — Inheritance, properties and ABCs; The data model; Descriptors and __slots__; Type hints and protocols; Functional tools; Generators in depth; Threads and futures; asyncio; Exceptions in depth; Performance

**Pro** (10) — Metaprogramming; Command-line tools; Testing strategy; Multiprocessing; An async network server; Memory and weak references; Build a mini ORM; Structured logging and context; A plugin architecture; Capstone: a persistent key-value store

**Exam - Certification** (6) — Six papers for the Python 3 Engineer Certification Basic Exam, weighted the way the real paper is: numbers, strings and lists; control flow and functions (the heaviest section); data structures; errors and exceptions; a standard library tour; modules, classes and I/O

**Exam - Review** (4) — Cumulative exams over the Beginner section, topics arriving mixed and unlabelled: values, text and decisions; collections and comprehensions; functions and failure; a class that saves itself


### CCNA

Networking for the CCNA 200-301 exam, configured with real IOS commands against
a simulator in `lib/netlab`. Lessons hand you `.ios` config files and are graded
on whether packets actually get through - including the return path, so a route
configured in one direction only fails the way it does on real kit.

**1. Network Fundamentals** (4) - Interfaces and addresses; Routing between two subnets; Subnetting without a calculator; Static routes and the return path

**2. Network Access** (4) - VLANs and access ports; Trunks between switches; Router on a stick; Layer 3 switching with SVIs

**3. IP Connectivity** (3) - OSPF in one area; How a router chooses; First hop redundancy with HSRP

**4. IP Services** (2) - NAT and the address you actually leave with; DHCP, NTP and logging

**5. Security Fundamentals** (3) - Standard access lists; Extended access lists; Port security and hardening the access layer

**6. Automation and Programmability** (1) - JSON, REST and talking to a controller

**Labs on real Linux** (3) - A real interface; Two hosts, one cable; A bridge is a switch

The labs leave the simulator behind and use the actual kernel: veth pairs,
network namespaces and bridges, with real ARP and real ICMP. They run inside
`unshare -Urn`, so they need no privileges and cannot touch the container's own
networking. Check what your kernel allows with `netlab ns`; the lessons skip
rather than fail where something is unavailable.

Explore a topology interactively from any terminal:

```bash
netlab topologies
netlab console two-routers R1
```

### Java

Java from the command line to the Oracle certifications and back to building
things, compiled and run for real with `javac` and the JUnit console launcher -
no Maven, no Gradle.

**Environment** (2) - javac, java and the classpath; Packages, imports and structure

**Silver** (8) - Primitives, casting and operator traps; Strings, immutability and StringBuilder; Control flow and switch; Arrays, multidimensional arrays and varargs; Methods, overloading and objects; Inheritance, overriding and interfaces; Exceptions, finally and try-with-resources; Wrappers, autoboxing and dates

**Silver - Practice exam** (4) - Types and flow; Strings, arrays and equality; Objects, inheritance and dispatch; Exceptions and the core APIs

**Gold** (8) - Generics and wildcards; The collections framework; Lambdas and functional interfaces; Streams; Optional; Threads, executors and safe sharing; Files, paths and NIO.2; Modules, annotations and reflection

**Gold - Practice exam** (3) - Generics and collections; Streams, lambdas and Optional; Concurrency, I/O and metadata

**Applied** (4) - Modelling a domain with types; Building a small service; Tests that let you change things; Capstone: a command line tool

### C

**Environment** (1) - The compiler, the linker and the binary

**Beginner** (6) - Types, sizes and integer behaviour; Pointers; Strings are arrays with a rule; Structs and how they are laid out; malloc, free and who owns what; Files, streams and checking every call

**Intermediate** (4) - Function pointers and dispatch tables; The preprocessor, and what a macro is not; Linked lists and the pointer-to-pointer idiom; Bits, masks and flags

**Advanced** (4) - A generic vector over void*; A hash table; Arena allocation; Capstone: a tokenizer

### C++

**Environment** (1) - What C++ adds, and what it keeps

**Beginner** (5) - vector, string and the range-for; Classes, constructors and RAII; Copies, moves and references; Templates, lambdas and the algorithms; Smart pointers and ownership

**Intermediate** (4) - Operator overloading; Runtime polymorphism; Reporting failure - exceptions, optional and expected; Iterators and ranges

**Advanced** (4) - A container with iterators; Concepts and constraints; Work done at compile time; Capstone: an expression evaluator

### C#

**Environment** (1) - The SDK, a project and the CLR

**Beginner** (3) - Classes, properties and records; Lists, dictionaries and the collection interfaces; LINQ

**Intermediate** (4) - Interfaces and generics; Records and pattern matching; Null, and when to throw; Delegates and events

**Advanced** (4) - Iterators and laziness; async and await; Structs and spans; Capstone: a log report

C and C++ are graded by `lib/ctest/ctest.h`, a single-header framework; C# by
`lib/csharp/LearnboxTest.cs`. Neither needs a package manager at check time.

### MATLAB

Aimed at the **MathWorks MATLAB Associate** (MLA-C01).

**Environment** (2) - MATLAB, and the engine under these lessons; Scripts, functions and the workspace

**Beginner** (6) - Arrays and indexing; Matrices, and the dot that changes everything; Logical indexing; Control flow; Function handles; Plotting

**Intermediate** (5) - Cell arrays and structs; Tables; datetime and duration; categorical; Importing and cleaning

**Advanced** (4) - Vectorisation; Errors and debugging; Text processing; Capstone: a readings report

**Associate - practice exam** (4) - The language and arrays; Importing and organising; Analysis and visualisation; Programming and debugging

The engine is **GNU Octave**: MATLAB is licensed per seat and has no headless
install. Octave runs the same core language, and `lib/octave` supplies the four
types it lacks - `string`, `table`, `datetime` and `categorical` - plus the
`lbx_*` grading harness, which emits the same JUnit XML as the other tracks.
`lib/octave/tests/run-all.sh` is that library's own regression suite.

One difference cannot be hidden: Octave has no string *literal*, so `"hi"` is a
char array there and lessons write `string('hi')` explicitly. Each shim's header
states where else it diverges. `install.sh --no-octave` skips the lot (620MB).

### Security

A hands-on cybersecurity track, from pure beginner to an advanced level, built
attack-then-defend: understand how something is attacked, then detect and fix
it. Every lab runs **inside this container and touches nothing outside it** -
the one rule the track opens with, since permission, not technique, is what
separates security work from a crime.

**Environment** (2) - the lab and the rule; reading bytes

**Foundations** (4) - encoding is not encryption; hashing and integrity; how passwords are stored and attacked; file permissions

**Cryptography** (6) - randomness; stream ciphers and nonce reuse; block modes; public-key RSA and Diffie-Hellman by hand; the certificate chain of trust

**Web security** (7) - the HTTP request; SQL injection; XSS; broken access control; path traversal; command injection; a vulnerable app to harden

**Network security** (6) - packets and ports; reading a capture; port scanning; ARP and DNS spoofing; a firewall rule engine

**Forensics** (6) - log analysis; magic bytes; metadata; hidden data; carving; timeline reconstruction

**Reading binaries** (5) - what an ELF is; strings and symbols; reading disassembly; dangerous patterns; the stack and overflows (stops at understanding, not exploitation)

**Defence and detection** (6) - hardening; detection rules; alert triage; file integrity monitoring; least-privilege review; incident response

**Challenges** (6) - unguided, mixed-topic problems pulling the whole track together

The whole track is pure-Python standard library and needs no extra toolchain:
the real tools (nmap, tcpdump, gdb, exiftool) are described for the free
terminal, but every graded lab reimplements their core, so a lesson can be
checked deterministically and nothing reaches outside the box. Each lab targets
a program that lives on `localhost` here, put there to practise on.

### Programming mindset

How to think while programming, practised in Python because the subject is not
the language.

**Thinking about problems** (2) - Decomposing a problem; From examples to rules

**Debugging and evidence** (2) - Reading the error; Hypotheses and bisection

**Craft** (2) - Naming and small functions; Knowing when to stop

### Rust

**Beginner** (12) — Hello, cargo; Variables and types; Control flow; Ownership; Borrowing and slices; Structs and methods; Enums and match; Option and Result; Vec, String and HashMap; Traits; Iterators and closures; Generics and lifetimes

**Intermediate** (10) — Modules and visibility; Designing errors; Traits in depth; Implementing iterators; Smart pointers; Patterns in depth; Strings and text; Closures in depth; Collections in depth; Lifetimes in depth

**Advanced** (10) — Threads; Channels; Shared state; Generics and typestate; Declarative macros; Conversions; Trees, graphs and Weak; I/O and files; A tokenizer and parser; Trait objects and dynamic dispatch

**Pro** (10) — Unsafe Rust; Futures by hand; A tiny executor; Atomics and lock-free code; Memory layout and allocation; Zero-copy parsing; FFI: calling C and being called; Designing a library API; Advanced traits; Capstone: a concurrent TCP server


## How it works

```
browser ──HTTP / WebSocket──▶ learnbox (Go, runs as root, systemd)
                                ├─ /api/term      bash in a PTY, as `learner`
                                ├─ /api/lessons   lesson text, workspace files, check, hint, reset
                                ├─ /metrics /healthz /readyz
                                └─ web/dist       Vite + TypeScript frontend
                              cgroup: learnbox.service/
                                ├─ app/           the service
                                └─ learner/       every shell and check: memory.max, pids.max
```

- **Workspaces** live in `/home/learner/learn/<lang>/<section>/<lesson>/`, or
  `/home/learner/profiles/<id>/learn/...` for a profile other than the first.
  The editor and the terminal work on the same files; the editor reloads files
  that change on disk.
- **Check** copies the workspace and the lesson's hidden tests to
  `~/.cache/learnbox/check/`, runs `pytest` or `cargo test` there as `learner`
  with a timeout, and parses the results per test.
- **Reset** moves the workspace to `~/learn/.reset-backups/` and restores the starter.
- **Progress** is one JSON file per profile in `/var/lib/learnbox`.
- **Terminal sessions** survive page changes: reopening a lesson reattaches to
  its shell and replays recent output.

### Profiles

The box starts with one profile, **Learner**, which owns the original
`progress.json` and `~/learn` - upgrading loses nothing, and a single person
never sees a profile prompt. Create more from the name button in the top bar.
Each profile has its own progress, its own copy of every lesson's files
(`~/profiles/<id>/learn`) and its own terminals. The browser remembers the
choice in a cookie; with several profiles and none picked, the app asks.

A profile is a preference, **not a login**. Anyone who can open the page can
pick any profile, and every profile runs as the same `learner` account, so one
person's shell can read another's files. That suits a household or a couple
of friends you trust. Strangers need real accounts - and, since the box hands
out a shell, separate system users or containers too - which this does not
attempt. Deleting a profile removes its progress and keeps its files.

### Safety model

One trusted user on a private network, so the goal is protecting the machine
from mistakes and from other websites, not from the user.

- The service runs as root; everything the learner runs is started as the
  unprivileged `learner` user (the kernel drops all capabilities on that switch)
  inside a cgroup with memory and process limits.
- File access inside the learner's home goes through `os.Root`, so a symlink
  planted in a workspace cannot redirect a root write outside it.
- Only IP addresses, `localhost`, the machine's hostname and
  `LEARNBOX_ALLOWED_HOSTS` are accepted in the `Host` header (DNS rebinding).
- Every non-GET request needs an `X-Learnbox: 1` header, and the terminal
  WebSocket checks `Origin` (cross-site requests from other tabs).
- Lesson Markdown is rendered with raw HTML disabled.

**Do not expose it to the internet without Cloudflare Access.** It hands out a
shell with no login of its own. LAN or Tailscale by default;
[docs/REMOTE-ACCESS.md](docs/REMOTE-ACCESS.md) covers the protected public
hostname, where learnbox verifies the Access token itself.

## Deploy

### Create the LXC

On a Proxmox host (needs `debian-13-standard` in `local`):

```bash
curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/create-lxc.sh
bash create-lxc.sh --ctid <id> --ip 192.168.0.<x>/24          # plan
bash create-lxc.sh --ctid <id> --ip 192.168.0.<x>/24 --yes    # create
```

It creates an unprivileged Debian 13 CT (2 cores, 2 GB RAM + 1 GB swap, 15 GB,
`nesting=1`), clones this repo to `/opt/learnbox` and runs the install. The
first install takes several minutes: it downloads the Rust toolchain, Go and
Node for the build, and both Exercism tracks.

Other flags: `--gw` (192.168.0.1), `--storage` (local-lvm), `--bridge` (vmbr0),
`--cores`, `--memory`, `--swap`, `--disk`, `--branch`.

Then open `http://<ip>:8080`. To use a hostname instead of the IP, add it to
`LEARNBOX_ALLOWED_HOSTS` in `/etc/learnbox.env` and `systemctl restart learnbox`.

### Update

On the Proxmox host:

```bash
curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/update-lxc.sh
bash update-lxc.sh --ctid <id> --snapshot --yes
```

Or inside the CT: `/opt/learnbox/scripts/update.sh`. An update pulls, rebuilds,
refreshes the Exercism import and restarts the service. It never touches
`/home/learner` or the profile and progress files in `/var/lib/learnbox`.

### Scripts

| Script | Runs on | Does |
|---|---|---|
| `scripts/create-lxc.sh` | Proxmox host | creates the CT, clones the repo, runs `install.sh` |
| `scripts/update-lxc.sh` | Proxmox host | optional snapshot, then `update.sh` inside the CT |
| `scripts/install.sh` | inside the CT | packages, learner user, Python venv, rustup, build, Exercism import, systemd unit |
| `scripts/update.sh` | inside the CT | `git pull --ff-only`, then `install.sh` |

`install.sh --no-rust`, `--no-java`, `--no-dotnet`, `--no-octave` and
`--no-exercism` skip those parts.

### Configuration

`/etc/learnbox.env`:

| Variable | Default | |
|---|---|---|
| `LEARNBOX_ADDR` | `:8080` | listen address |
| `LEARNBOX_ALLOWED_HOSTS` | | extra hostnames, comma separated |
| `LEARNBOX_MEMORY_MAX` | `1200M` | cgroup `memory.max` for all learner processes |
| `LEARNBOX_SWAP_MAX` | `512M` | cgroup `memory.swap.max` |
| `LEARNBOX_PIDS_MAX` | `512` | cgroup `pids.max` |
| `LEARNBOX_CPU_MAX` | `150%` | cgroup `cpu.max`, as a percentage of one core |
| `LEARNBOX_MAX_SESSIONS` | `8` | terminals; the oldest detached one is evicted past this |
| `LEARNBOX_IDLE_TIMEOUT` | `4h` | detached sessions are killed after this |
| `LEARNBOX_MIN_FREE_MB` | `512` | refuse new shells and checks below this much free space |
| `LEARNBOX_CHECK_TIMEOUT` | `120s` | per check; the first Rust build of a lesson is the slow one |
| `LEARNBOX_ACCESS_HOSTS` | | public hostnames that must present a Cloudflare Access token |
| `LEARNBOX_ACCESS_TEAM_DOMAIN` | | `<team>.cloudflareaccess.com` |
| `LEARNBOX_ACCESS_AUD` | | the Access application's audience tag |

Two of these are worth understanding rather than just setting:

- **`LEARNBOX_SWAP_MAX` is what makes the memory cap real.** With swap left
  uncapped a process over `memory.max` is swapped rather than killed, so it
  survives and the box crawls. Measured: a 256 MB allocation against a 64 MB
  cap succeeds with swap uncapped, and is killed with `memory.swap.max=0`.
- **`LEARNBOX_CPU_MAX` needs the `cpu` controller delegated to the container.**
  Where it is not, learnbox logs `cpu controller not delegated; learner CPU is
  uncapped` at start and `learnbox_cpu_capped` reads 0. The unit's
  `CPUQuota=180%` is the backstop; alert on the metric rather than assuming.

A hostname in `LEARNBOX_ACCESS_HOSTS` is refused (503) until the team domain and
audience are set, so a half-finished setup cannot expose a shell. See
[docs/REMOTE-ACCESS.md](docs/REMOTE-ACCESS.md) for the full path through
Cloudflare Access, the tunnel and Caddy.

### Layout inside the CT

| Path | Owner | Purpose |
|---|---|---|
| `/opt/learnbox` | root | this repo, `bin/learnbox`, `web/dist` |
| `/opt/learnbox-toolchain` | root | Go and Node, used only to build |
| `/var/lib/learnbox` | root | `profiles.json`, `progress*.json` (one per profile), Exercism checkouts and import |
| `/home/learner` | learner | workspaces, `.venv` (pytest), `.cargo` / `.rustup` |

### Monitoring

The service follows the homelab monitoring service contract: `GET /healthz`,
`GET /readyz`, `GET /metrics` on port 8080, JSON logs to stdout.

Exposing the metrics is not the same as collecting them. Register the target in
the **mon LXC** (`192.168.0.200`), not in this repo — vmagent reloads the file
within 60 s, no restart:

```bash
# in the mon LXC, appending to /srv/monitoring/targets/services.json
{ "targets": ["192.168.0.116:8080"],
  "labels": { "job": "service", "service": "learnbox", "kind": "lxc" } }
```

Confirm it landed:

```bash
curl -s 'http://192.168.0.200:8428/api/v1/query?query=learnbox_build_info' | grep -o '"commit":"[^"]*"'
```

The host allowlist does not block this: requests to a bare IP are always
accepted, so scraping works without listing the mon LXC anywhere. Ship logs with
`setup-guest-logging.sh --only <ctid>`.

## Writing lessons

Sections are `learn` (shown as Beginner), `intermediate`, `advanced`, `pro` and
`practice` (generated from Exercism). A lesson is a directory under
`content/<lang>/<section>/<slug>/`:

```
lesson.md    front matter + Markdown explanation
starter/     copied into the workspace the first time the lesson opens
tests/       hidden tests: pytest files for Python, tests/*.rs for Rust
solution/    reference answer, overlaid on starter by `learnbox verify`
```

```yaml
---
title: Loops
summary: One line for the lesson list.
order: 6
files: [loops.py]        # editable files, in tab order
run: python -i loops.py  # what the Run button types into the terminal
hints:
  - "First hint, Markdown allowed."
  - "Second hint."
---
```

Check that every reference solution passes (inside the CT):

```bash
LEARNBOX_CONTENT=/opt/learnbox/content /opt/learnbox/bin/learnbox verify python/learn
```

`verify` also runs the examples in a lesson's prose, so a lesson that says
"this prints 2790" is checked, not trusted. Two formats opt an example in.

A **program and its output**, in any track: a complete program in the track's
language (Python for CCNA, mindset and security) directly followed - nothing
but blank lines between - by an ` ```output ` block. `verify` compiles it the
way the lesson checks do (gcc `-std=c17`, g++ `-std=c++20`, rustc edition 2024,
single-file `java`, a net8.0 project, Octave), runs it and compares its standard
output. The learner sees the block labelled **Output**.

````markdown
```c
#include <stdio.h>
int main(void) { printf("%d\n", 6 * 7); }
```

```output
42
```
````

An **interactive transcript**, in the Python-based tracks: a ` ```pycon `
block, run as a doctest. The transcripts in one lesson share their names, top
to bottom, the way a reader follows them.

````markdown
```pycon
>>> pow(65, 17, 3233)
2790
```
````

Both run beside a copy of the reference solution, so an example can `import`
the module the learner writes. In expected output `...` matches anything, e.g.
`'...'` for a random token; trailing spaces never matter, and for MATLAB
neither does spacing (Octave lays values out differently). A program must exit
with status 0. A failure names the lesson.md line.

Blocks without one of these formats are not run: many are fragments that only
make sense in context. None of this happens in a learner's **Check**.

## Development

```bash
go build ./cmd/learnbox                     # Linux only (PTYs, cgroups)
cd web && npm install && npm run dev        # proxies /api to LEARNBOX_API (default localhost:8080)
```

## Credits

Practice exercises: [Exercism](https://github.com/exercism) Python and Rust
tracks, MIT License, imported at install time and not redistributed here.
Learn lessons are original to this project.
