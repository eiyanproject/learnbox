"""Command line: an interactive IOS console over a named topology.

    python -m netlab console two-routers R1
    python -m netlab topologies
    python -m netlab check two-routers PC1 PC2
    python -m netlab ns                    what real network namespaces allow here

The console is the point: a learner should be able to type the same commands
they would type on real kit and watch the prompt change between modes. Config
made here is kept in memory only - each run starts from the shipped topology,
which is what makes a lesson repeatable.
"""

from __future__ import annotations

import sys

from .ios import Console
from .topologies import names, topology


def _console(topo_name: str, device: str) -> int:
    lab = topology(topo_name)
    con = Console(lab, device)
    print(f"netlab: {topo_name}, device {device}. Ctrl-D to leave; 'show ip interface brief' to look around.")
    while True:
        try:
            line = input(con.prompt + " ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line.strip() in ("quit", "logout"):
            return 0
        out = con.run(line)
        if out:
            print(out)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]

    if cmd == "topologies":
        for n in names():
            lab = topology(n)
            print(f"{n:<14} {len(lab.devices)} devices: {', '.join(lab.devices)}")
        return 0

    if cmd == "console":
        if len(rest) != 2:
            print("usage: python -m netlab console <topology> <device>", file=sys.stderr)
            return 2
        return _console(rest[0], rest[1])

    if cmd == "ns":
        from . import ns as nsmod

        caps = nsmod.capabilities()
        width = max(len(k) for k in caps)
        for name, ok in caps.items():
            print(f"  {name:<{width}}  {'yes' if ok else 'no'}")
        if not caps["netns"]:
            print()
            print("Unprivileged network namespaces are not available here.")
            print("On Proxmox the container needs nesting=1.")
            return 1
        print()
        print("Try a lab shell:  unshare -Urn bash")
        return 0

    if cmd == "check":
        if len(rest) != 3:
            print("usage: python -m netlab check <topology> <src> <dst>", file=sys.stderr)
            return 2
        lab = topology(rest[0])
        res = lab.ping(rest[1], rest[2])
        print(f"{'reachable' if res.ok else 'unreachable'}: {' -> '.join(res.path) or '-'}")
        if not res.ok:
            print(f"  {res.reason}")
        return 0 if res.ok else 1

    print(f"unknown command {cmd!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
