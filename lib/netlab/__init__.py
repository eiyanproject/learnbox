"""netlab - a small Cisco-shaped network simulator for the learnbox CCNA track.

Typical use in a lesson test:

    from netlab import Lab, apply_config, topology

    lab = topology("two-routers")
    errors = apply_config(lab, "R1", open("r1.ios").read())
    assert errors == []
    assert lab.ping("PC1", "PC2")

and interactively, from the terminal:

    netlab console two-routers R1
"""

from .ios import Console, apply_config
from .lesson import build, report
from .lab import Lab, PingResult, TraceHop
from . import ns
from .model import ConfigError, Device, Host, Interface, Router, Switch
from .topologies import names as topology_names, topology

__all__ = [
    "Lab",
    "Console",
    "apply_config",
    "build",
    "report",
    "topology",
    "topology_names",
    "PingResult",
    "TraceHop",
    "Device",
    "Router",
    "Switch",
    "Host",
    "Interface",
    "ConfigError",
    "ns",
]
