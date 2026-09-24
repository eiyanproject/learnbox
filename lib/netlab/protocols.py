"""Protocols that change where a packet goes: OSPF, ACLs, NAT and HSRP.

These live apart from the plain forwarding model because each is a decision
layered on top of it - OSPF fills the routing table, an ACL vetoes a packet the
table would have forwarded, NAT rewrites it on the way past, and HSRP puts a
virtual address in front of a real one.

Simplifications, stated plainly so lessons do not imply more than is modelled:

  - OSPF: single area, no LSA types, no DR/BDR election, no timers. Routers
    that share a subnet and have `network` statements covering it become
    neighbours immediately, and routes are shortest-total-cost. That is enough
    to teach what `network` and wildcard masks do and to make a missing
    statement visibly break something.
  - ACLs: matched per packet on the interface they are applied to, in the
    direction they are applied. Standard ACLs match source only; extended match
    source, destination and protocol. Implicit deny at the end, as on real kit.
  - NAT: source translation on inside-to-outside. Static entries and overload
    (PAT) onto an interface address.
  - HSRP: the highest priority among routers sharing a group owns the virtual
    IP. No hellos, no preempt delay.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

__all__ = ["ACL", "ACLEntry", "NAT", "OSPF", "HSRPGroup", "DHCPPool", "wildcard_to_network"]


def wildcard_to_network(address: str, wildcard: str) -> ipaddress.IPv4Network:
    """
    Turn "10.0.0.0 0.0.0.255" into 10.0.0.0/24.

    A wildcard mask is the bitwise inverse of a subnet mask, which is the thing
    everyone gets wrong first: 0 means "must match", 1 means "don't care".
    """
    inverted = ".".join(str(255 - int(octet)) for octet in wildcard.split("."))
    return ipaddress.ip_network(f"{address}/{inverted}", strict=False)


# ---------------------------------------------------------------- ACLs


@dataclass
class ACLEntry:
    action: str  # permit | deny
    protocol: str  # ip | icmp | tcp | udp
    source: ipaddress.IPv4Network
    destination: ipaddress.IPv4Network | None = None

    def matches(self, src: str, dst: str, protocol: str = "icmp") -> bool:
        if self.protocol not in ("ip", protocol):
            return False
        if ipaddress.ip_address(src) not in self.source:
            return False
        if self.destination is not None and ipaddress.ip_address(dst) not in self.destination:
            return False
        return True


@dataclass
class ACL:
    name: str
    entries: list[ACLEntry] = field(default_factory=list)

    def permits(self, src: str, dst: str, protocol: str = "icmp") -> bool:
        for entry in self.entries:
            if entry.matches(src, dst, protocol):
                return entry.action == "permit"
        # Every access list ends in an invisible "deny any". An ACL that
        # permits nothing explicitly therefore blocks everything, which is the
        # classic way to lock yourself out of a lab.
        return False


# ---------------------------------------------------------------- NAT


@dataclass
class NAT:
    static: dict[str, str] = field(default_factory=dict)  # inside local -> inside global
    overload_acl: str | None = None
    overload_interface: str | None = None

    def translate(self, src: str, outside_ip: str | None) -> str:
        if src in self.static:
            return self.static[src]
        if self.overload_interface and outside_ip:
            return outside_ip
        return src


# ---------------------------------------------------------------- OSPF


@dataclass
class OSPF:
    process: int
    networks: list[tuple[ipaddress.IPv4Network, int]] = field(default_factory=list)  # (network, area)
    router_id: str | None = None

    def covers(self, ip: str) -> bool:
        """Is this interface address inside one of the network statements?"""
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net, _ in self.networks)


# ---------------------------------------------------------------- HSRP


@dataclass
class HSRPGroup:
    group: int
    virtual_ip: str
    priority: int = 100
    preempt: bool = False


# ---------------------------------------------------------------- DHCP


@dataclass
class DHCPPool:
    name: str
    network: ipaddress.IPv4Network | None = None
    default_router: str | None = None
    dns_server: str | None = None
