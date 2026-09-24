"""The bridge between a lesson's config files and its tests.

A CCNA lesson hands the learner one `.ios` file per device. Both the test and
the `python lab.py` the learner runs themselves go through `build`, so the
feedback in the terminal and the grade from Check can never disagree.
"""

from __future__ import annotations

import pathlib

from .ios import apply_config
from .lab import Lab
from .topologies import topology

__all__ = ["build", "report"]


def build(topo: str, configs: dict[str, str], directory: str = ".") -> tuple[Lab, list[str]]:
    """
    Load a topology and apply one config file per device.

    `configs` maps device name to filename, e.g. {"R1": "r1.ios"}. A missing
    file is an error rather than an empty config: silently treating it as blank
    would report "no route" when the real problem is a typo in the filename.
    """
    lab = topology(topo)
    errors: list[str] = []
    base = pathlib.Path(directory)
    for device, filename in configs.items():
        path = base / filename
        if not path.exists():
            errors.append(f"{filename}: no such file")
            continue
        errors.extend(f"{filename}: {e}" for e in apply_config(lab, device, path.read_text(encoding="utf-8")))
    return lab, errors


def report(topo: str, configs: dict[str, str], checks: list[tuple[str, str]], directory: str = ".") -> int:
    """
    Print what the learner's config achieves. Returns a process exit code.

    This is what `python lab.py` runs, and it deliberately prints the path a
    working ping took: seeing "PC1 -> R1 -> R2 -> PC2" is how the topology
    stops being an abstraction.
    """
    lab, errors = build(topo, configs, directory)

    if errors:
        print("Configuration problems:")
        for e in errors:
            print(f"  {e}")
        print()

    width = max((len(f"{a} -> {b}") for a, b in checks), default=10)
    failures = 0
    for src, dst in checks:
        result = lab.ping(src, dst)
        label = f"{src} -> {dst}"
        if result.ok:
            print(f"  {label:<{width}}  reachable   {' -> '.join(result.path)}")
        else:
            failures += 1
            print(f"  {label:<{width}}  UNREACHABLE {result.reason}")

    print()
    if errors:
        print(f"{len(errors)} configuration line(s) IOS would reject.")
    print(f"{len(checks) - failures}/{len(checks)} reachable.")
    return 1 if (failures or errors) else 0
