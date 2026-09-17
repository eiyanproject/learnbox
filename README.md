# learnbox

A private, single-user learning platform for Python and Rust. Each lesson is an
explanation on the left and a real workspace on the right: a code editor over a
real `bash` terminal, hidden tests behind a **Check** button, and hints when you
are stuck. Everything runs in one small LXC on your own network.

- **Learn**: 12 guided Python lessons and 12 guided Rust lessons, written for this project
- **Practice**: ~130 Python and ~90 Rust exercises imported from [Exercism](https://exercism.org) (MIT)
- **Terminal**: a free scratch shell with `python`, `cargo` and `git`

Styling follows the *Recipe Catalog Terminal* Claude Design canvas: cyan as the
one accent, magenta for passed work, amber for shortfalls, Chakra Petch and IBM
Plex Mono. Dark and light themes.

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

- **Workspaces** live in `/home/learner/learn/<lang>/<section>/<lesson>/`. The
  editor and the terminal work on the same files; the editor reloads files that
  change on disk.
- **Check** copies the workspace and the lesson's hidden tests to
  `~/.cache/learnbox/check/`, runs `pytest` or `cargo test` there as `learner`
  with a timeout, and parses the results per test.
- **Reset** moves the workspace to `~/learn/.reset-backups/` and restores the starter.
- **Progress** is one JSON file, `/var/lib/learnbox/progress.json`.
- **Terminal sessions** survive page changes: reopening a lesson reattaches to
  its shell and replays recent output.

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

**Do not expose it to the internet.** It hands out a shell with no login. Use
LAN or Tailscale.

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
`/home/learner` or `/var/lib/learnbox/progress.json`.

### Scripts

| Script | Runs on | Does |
|---|---|---|
| `scripts/create-lxc.sh` | Proxmox host | creates the CT, clones the repo, runs `install.sh` |
| `scripts/update-lxc.sh` | Proxmox host | optional snapshot, then `update.sh` inside the CT |
| `scripts/install.sh` | inside the CT | packages, learner user, Python venv, rustup, build, Exercism import, systemd unit |
| `scripts/update.sh` | inside the CT | `git pull --ff-only`, then `install.sh` |

`install.sh --no-rust` and `--no-exercism` skip those parts.

### Configuration

`/etc/learnbox.env`:

| Variable | Default | |
|---|---|---|
| `LEARNBOX_ADDR` | `:8080` | listen address |
| `LEARNBOX_ALLOWED_HOSTS` | | extra hostnames, comma separated |
| `LEARNBOX_MEMORY_MAX` | `1200M` | cgroup `memory.max` for all learner processes |
| `LEARNBOX_SWAP_MAX` | `512M` | cgroup `memory.swap.max` |
| `LEARNBOX_PIDS_MAX` | `512` | cgroup `pids.max` |
| `LEARNBOX_CHECK_TIMEOUT` | `120s` | per check; the first Rust build of a lesson is the slow one |

### Layout inside the CT

| Path | Owner | Purpose |
|---|---|---|
| `/opt/learnbox` | root | this repo, `bin/learnbox`, `web/dist` |
| `/opt/learnbox-toolchain` | root | Go and Node, used only to build |
| `/var/lib/learnbox` | root | `progress.json`, Exercism checkouts and import |
| `/home/learner` | learner | workspaces, `.venv` (pytest), `.cargo` / `.rustup` |

### Monitoring

The service follows the homelab monitoring service contract: `GET /healthz`,
`GET /readyz`, `GET /metrics` on port 8080, JSON logs to stdout. Register it in
the monitoring repo's `targets/services.json`, and ship logs with
`setup-guest-logging.sh --only <ctid>`.

## Writing lessons

A lesson is a directory under `content/<lang>/<section>/<slug>/`:

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

## Development

```bash
go build ./cmd/learnbox                     # Linux only (PTYs, cgroups)
cd web && npm install && npm run dev        # proxies /api to LEARNBOX_API (default localhost:8080)
```

## Credits

Practice exercises: [Exercism](https://github.com/exercism) Python and Rust
tracks, MIT License, imported at install time and not redistributed here.
Learn lessons are original to this project.
