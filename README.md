# learnbox

Private, single-user learning platform for Python (first) and Rust (later).
Lessons with explanation on the left, editor + real terminal on the right,
hidden tests and hints for guided exercises. Runs in one LXC, reachable over
LAN / Tailscale only.

## Stack

- Backend: Go (single binary) — terminal over WebSocket, workspace files, test runner, SQLite progress
- Frontend: Vite + TypeScript, CodeMirror 6, xterm.js
- Content: Markdown lessons, adapted from Exercism / Rustlings (MIT), Python tutorial (PSF), Rust Book (MIT/Apache)

## Phases

1. **LXC setup** — `scripts/` ← done
2. App skeleton + web terminal
3. Lesson renderer, editor, workspace file sync
4. Check / hints / reset / progress
5. Content import + first lessons (Python)
6. Rust toolchain and lessons

## Scripts

| Script | Runs on | Does |
|---|---|---|
| `scripts/create-lxc.sh` | Proxmox host | creates the CT, clones this repo to `/opt/learnbox`, runs `install.sh` |
| `scripts/update-lxc.sh` | Proxmox host | optional snapshot, then runs `update.sh` inside the CT |
| `scripts/install.sh` | inside the CT | packages, users, Python env (idempotent) |
| `scripts/update.sh` | inside the CT | `git pull --ff-only`, then re-runs `install.sh` |

The host scripts are standalone and print a plan until you pass `--yes`.

### Create

On the Proxmox host:

```bash
curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/create-lxc.sh
bash create-lxc.sh --ctid <id> --ip 192.168.0.<x>/24          # plan
bash create-lxc.sh --ctid <id> --ip 192.168.0.<x>/24 --yes    # create
```

Uses the newest `debian-13-standard` template already in `local` (no download)
and checks the CTID cluster-wide. Other flags: `--gw` (192.168.0.1), `--storage`
(local-lvm), `--bridge` (vmbr0), `--cores` 2, `--memory` 2048, `--swap` 1024,
`--disk` 15, `--branch` main.

### Update

On the Proxmox host:

```bash
curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/update-lxc.sh
bash update-lxc.sh --ctid <id> --snapshot --yes
```

Or inside the CT: `/opt/learnbox/scripts/update.sh`. Updates never touch
`/home/learner` or `/var/lib/learnbox`.

## Layout inside the CT

| Path | Owner | Purpose |
|---|---|---|
| `/home/learner` | learner | web shell user; `~/learn/<lang>/<lesson>/` workspaces, `~/scratch` |
| `/home/learner/.venv` | learner | Python venv with pytest, auto-activated in every shell |
| `/opt/learnbox` | root | app binary + built frontend + lessons (read-only to learner) |
| `/var/lib/learnbox` | learnbox | SQLite progress DB |

Memory / process caps for the shell are applied by the service in phase 2
(it spawns the shell into its own delegated cgroup), not here.
