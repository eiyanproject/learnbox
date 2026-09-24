"""Named topologies the lessons build on.

Each is deliberately unconfigured: interfaces are shut, routers have no
addresses, and switch ports are all in VLAN 1. The lesson's job is to make it
work, so the starting state has to be the state a real device ships in.
"""

from __future__ import annotations

from .lab import Lab

__all__ = ["topology", "names"]


def _one_router() -> Lab:
    """PC1 --- R1 --- PC2. Two subnets, one router. The first routing lesson."""
    lab = Lab()
    lab.router("R1", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.host("PC1", "192.168.1.10", "255.255.255.0", "192.168.1.1")
    lab.host("PC2", "192.168.2.10", "255.255.255.0", "192.168.2.1")
    lab.link("PC1:Ethernet0", "R1:GigabitEthernet0/0")
    lab.link("PC2:Ethernet0", "R1:GigabitEthernet0/1")
    return lab


def _two_routers() -> Lab:
    """PC1 -- R1 == R2 -- PC2, with a /30 between the routers: static routing."""
    lab = Lab()
    lab.router("R1", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.router("R2", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.host("PC1", "192.168.1.10", "255.255.255.0", "192.168.1.1")
    lab.host("PC2", "192.168.3.10", "255.255.255.0", "192.168.3.1")
    lab.link("PC1:Ethernet0", "R1:GigabitEthernet0/0")
    lab.link("R1:GigabitEthernet0/1", "R2:GigabitEthernet0/1")
    lab.link("R2:GigabitEthernet0/0", "PC2:Ethernet0")
    return lab


def _switched() -> Lab:
    """Four PCs on one switch: the VLAN lessons."""
    lab = Lab()
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3", "FastEthernet0/4")
    for n, ip in enumerate(["10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"], start=1):
        lab.host(f"PC{n}", ip, "255.255.255.0")
        lab.link(f"PC{n}:Ethernet0", f"SW1:FastEthernet0/{n}")
    return lab


def _two_switches() -> Lab:
    """Two switches with a link between them: trunking, and why it is needed."""
    lab = Lab()
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "GigabitEthernet0/1")
    lab.switch("SW2", "FastEthernet0/1", "FastEthernet0/2", "GigabitEthernet0/1")
    lab.host("PC1", "10.0.10.11", "255.255.255.0")
    lab.host("PC2", "10.0.20.11", "255.255.255.0")
    lab.host("PC3", "10.0.10.12", "255.255.255.0")
    lab.host("PC4", "10.0.20.12", "255.255.255.0")
    lab.link("PC1:Ethernet0", "SW1:FastEthernet0/1")
    lab.link("PC2:Ethernet0", "SW1:FastEthernet0/2")
    lab.link("PC3:Ethernet0", "SW2:FastEthernet0/1")
    lab.link("PC4:Ethernet0", "SW2:FastEthernet0/2")
    lab.link("SW1:GigabitEthernet0/1", "SW2:GigabitEthernet0/1")
    return lab


def _branch() -> Lab:
    """A three-router chain: default routes, and where traffic actually goes."""
    lab = Lab()
    for name in ("R1", "R2", "R3"):
        lab.router(name, "GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2")
    lab.host("PC1", "172.16.1.10", "255.255.255.0", "172.16.1.1")
    lab.host("SRV", "172.16.9.10", "255.255.255.0", "172.16.9.1")
    lab.link("PC1:Ethernet0", "R1:GigabitEthernet0/0")
    lab.link("R1:GigabitEthernet0/1", "R2:GigabitEthernet0/1")
    lab.link("R2:GigabitEthernet0/2", "R3:GigabitEthernet0/2")
    lab.link("R3:GigabitEthernet0/0", "SRV:Ethernet0")
    return lab


_BUILDERS = {
    "one-router": _one_router,
    "two-routers": _two_routers,
    "switched": _switched,
    "two-switches": _two_switches,
    "branch": _branch,
}


def names() -> list[str]:
    return sorted(_BUILDERS)


def topology(name: str) -> Lab:
    if name not in _BUILDERS:
        raise KeyError(f"no topology {name!r}; try one of {', '.join(names())}")
    return _BUILDERS[name]()


def _router_on_a_stick() -> Lab:
    """One switch, two VLANs, one router link: the classic inter-VLAN setup."""
    lab = Lab()
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "GigabitEthernet0/1")
    lab.router("R1", "GigabitEthernet0/0")
    lab.host("PC1", "10.0.10.11", "255.255.255.0", "10.0.10.1")
    lab.host("PC2", "10.0.20.11", "255.255.255.0", "10.0.20.1")
    lab.link("PC1:Ethernet0", "SW1:FastEthernet0/1")
    lab.link("PC2:Ethernet0", "SW1:FastEthernet0/2")
    lab.link("SW1:GigabitEthernet0/1", "R1:GigabitEthernet0/0")
    return lab


def _triangle() -> Lab:
    """Three routers in a ring: OSPF has a choice of paths, so cost matters."""
    lab = Lab()
    for name in ("R1", "R2", "R3"):
        lab.router(name, "GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2")
    lab.host("PC1", "192.168.1.10", "255.255.255.0", "192.168.1.1")
    lab.host("PC3", "192.168.3.10", "255.255.255.0", "192.168.3.1")
    lab.link("PC1:Ethernet0", "R1:GigabitEthernet0/0")
    lab.link("PC3:Ethernet0", "R3:GigabitEthernet0/0")
    lab.link("R1:GigabitEthernet0/1", "R2:GigabitEthernet0/1")
    lab.link("R2:GigabitEthernet0/2", "R3:GigabitEthernet0/2")
    return lab


def _edge() -> Lab:
    """An inside LAN, an edge router, and a server out on the internet: NAT and ACLs."""
    lab = Lab()
    lab.router("EDGE", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.router("ISP", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "GigabitEthernet0/1")
    lab.host("PC1", "192.168.10.11", "255.255.255.0", "192.168.10.1")
    lab.host("PC2", "192.168.10.12", "255.255.255.0", "192.168.10.1")
    lab.host("WEB", "8.8.8.8", "255.255.255.0", "8.8.8.1")
    lab.link("PC1:Ethernet0", "SW1:FastEthernet0/1")
    lab.link("PC2:Ethernet0", "SW1:FastEthernet0/2")
    lab.link("SW1:GigabitEthernet0/1", "EDGE:GigabitEthernet0/0")
    lab.link("EDGE:GigabitEthernet0/1", "ISP:GigabitEthernet0/1")
    lab.link("ISP:GigabitEthernet0/0", "WEB:Ethernet0")
    return lab


def _l3_switch() -> Lab:
    """A layer 3 switch doing inter-VLAN routing with SVIs."""
    lab = Lab()
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3")
    lab.host("PC1", "10.0.10.11", "255.255.255.0", "10.0.10.1")
    lab.host("PC2", "10.0.20.11", "255.255.255.0", "10.0.20.1")
    lab.host("PC3", "10.0.10.12", "255.255.255.0", "10.0.10.1")
    lab.link("PC1:Ethernet0", "SW1:FastEthernet0/1")
    lab.link("PC2:Ethernet0", "SW1:FastEthernet0/2")
    lab.link("PC3:Ethernet0", "SW1:FastEthernet0/3")
    return lab


_BUILDERS.update(
    {
        "router-on-a-stick": _router_on_a_stick,
        "triangle": _triangle,
        "edge": _edge,
        "l3-switch": _l3_switch,
    }
)


def _redundant() -> Lab:
    """Two routers offering one gateway address to a LAN: HSRP."""
    lab = Lab()
    lab.switch("SW1", "FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3")
    lab.router("R1", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.router("R2", "GigabitEthernet0/0", "GigabitEthernet0/1")
    lab.router("CORE", "GigabitEthernet0/1", "GigabitEthernet0/2", "GigabitEthernet0/3")
    lab.host("PC1", "192.168.1.10", "255.255.255.0", "192.168.1.254")
    lab.host("SRV", "10.10.10.10", "255.255.255.0", "10.10.10.1")
    lab.link("PC1:Ethernet0", "SW1:FastEthernet0/1")
    lab.link("SW1:FastEthernet0/2", "R1:GigabitEthernet0/0")
    lab.link("SW1:FastEthernet0/3", "R2:GigabitEthernet0/0")
    lab.link("R1:GigabitEthernet0/1", "CORE:GigabitEthernet0/1")
    lab.link("R2:GigabitEthernet0/1", "CORE:GigabitEthernet0/2")
    lab.link("CORE:GigabitEthernet0/3", "SRV:Ethernet0")
    return lab


_BUILDERS["redundant"] = _redundant
