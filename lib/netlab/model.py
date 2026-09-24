"""The network itself: devices, links, and whether a packet gets through.

The model is deliberately a layer below the CLI. IOS syntax is a way of editing
this state, not the state itself, so the same topology can be driven from a
lesson's test, from a config file, or from the interactive console, and all
three agree about what "reachable" means.

What is simulated, and what is not:

  - Layer 2: links, switches, VLANs, access and trunk ports. A broadcast domain
    is worked out by walking links through switches, honouring VLAN membership.
  - Layer 3: interface addresses, connected routes, static routes, a default
    route, and longest-prefix matching.
  - ICMP: ping and traceroute walk the path hop by hop, so a missing return
    route fails the way it does on real kit - which is the single most common
    thing a CCNA candidate gets wrong.

  - Not simulated: timing, MTU, fragmentation, queueing, STP convergence,
    dynamic routing protocols. Those would add behaviour a lesson cannot
    assert on deterministically.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

__all__ = [
    "Interface",
    "Device",
    "Router",
    "Switch",
    "Host",
    "Lab",
    "PingResult",
    "ConfigError",
]


class ConfigError(Exception):
    """A configuration that real IOS would reject."""


def _net(ip: str, mask: str) -> ipaddress.IPv4Network:
    """The network an address sits in. Accepts a dotted mask or a prefix length."""
    if mask.isdigit():
        return ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    return ipaddress.ip_network(f"{ip}/{mask}", strict=False)


@dataclass(eq=False)
class Interface:
    name: str
    device: "Device"
    ip: str | None = None
    mask: str | None = None
    # Real interfaces start administratively down; forgetting "no shutdown" is
    # a rite of passage, so the simulator keeps it.
    shutdown: bool = True
    # Switch ports only.
    mode: str = "access"  # access | trunk
    vlan: int = 1
    trunk_vlans: set[int] | None = None
    description: str = ""
    link: "Interface | None" = None

    @property
    def up(self) -> bool:
        """Up means configured up at both ends and actually cabled."""
        return not self.shutdown and self.link is not None and not self.link.shutdown

    @property
    def network(self) -> ipaddress.IPv4Network | None:
        if not self.ip or not self.mask:
            return None
        return _net(self.ip, self.mask)

    def carries(self, vlan: int) -> bool:
        """Does this switch port pass the given VLAN?"""
        if self.mode == "trunk":
            return self.trunk_vlans is None or vlan in self.trunk_vlans
        return self.vlan == vlan

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Interface {self.device.name}/{self.name} {self.ip or 'unassigned'}>"


@dataclass
class Route:
    network: ipaddress.IPv4Network
    next_hop: str | None  # None for a connected route
    interface: str | None
    source: str  # "C" connected, "S" static

    @property
    def prefix_len(self) -> int:
        return self.network.prefixlen


@dataclass(eq=False)
class Device:
    name: str
    interfaces: dict[str, Interface] = field(default_factory=dict)
    hostname: str = ""

    def __post_init__(self) -> None:
        self.hostname = self.hostname or self.name

    def interface(self, name: str) -> Interface:
        """Look up an interface, accepting the abbreviations IOS accepts."""
        name = normalise_ifname(name)
        if name not in self.interfaces:
            raise ConfigError(f"{self.hostname}: no interface {name}")
        return self.interfaces[name]

    def add_interface(self, name: str) -> Interface:
        name = normalise_ifname(name)
        iface = Interface(name=name, device=self)
        self.interfaces[name] = iface
        return iface

    def addresses(self) -> list[Interface]:
        return [i for i in self.interfaces.values() if i.ip and i.up]


# IOS lets you type "g0/0" for "GigabitEthernet0/0"; lessons and tests should
# accept the same shorthand or the simulator feels fake in a way that matters.
_PREFIXES = [
    ("gigabitethernet", "GigabitEthernet"),
    ("fastethernet", "FastEthernet"),
    ("ethernet", "Ethernet"),
    ("serial", "Serial"),
    ("loopback", "Loopback"),
    ("vlan", "Vlan"),
]


def normalise_ifname(name: str) -> str:
    raw = name.strip()
    lowered = raw.lower()
    for short, full in _PREFIXES:
        # Match the longest unambiguous prefix the user typed: "gi0/1", "g0/1".
        for cut in range(len(short), 0, -1):
            token = short[:cut]
            if lowered.startswith(token):
                rest = raw[cut:]
                if rest and (rest[0].isdigit() or rest[0] == " "):
                    return full + rest.strip()
    return raw


@dataclass(eq=False)
class Router(Device):
    static_routes: list[Route] = field(default_factory=list)
    ip_routing: bool = True

    def routing_table(self) -> list[Route]:
        """Connected routes plus statics, longest prefix first - as `show ip route`."""
        table: list[Route] = []
        for iface in self.interfaces.values():
            if iface.ip and iface.up and iface.network:
                table.append(Route(iface.network, None, iface.name, "C"))
        table.extend(self.static_routes)
        return sorted(table, key=lambda r: r.prefix_len, reverse=True)

    def lookup(self, dst: str) -> Route | None:
        addr = ipaddress.ip_address(dst)
        for route in self.routing_table():
            if addr in route.network:
                return route
        return None


@dataclass(eq=False)
class Switch(Device):
    vlans: dict[int, str] = field(default_factory=lambda: {1: "default"})

    def add_vlan(self, vid: int, name: str = "") -> None:
        if not 1 <= vid <= 4094:
            raise ConfigError(f"VLAN id {vid} is out of range (1-4094)")
        self.vlans[vid] = name or f"VLAN{vid:04d}"


@dataclass(eq=False)
class Host(Device):
    gateway: str | None = None

    @property
    def iface(self) -> Interface:
        return next(iter(self.interfaces.values()))
