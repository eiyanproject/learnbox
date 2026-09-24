"""Putting devices together and moving packets between them.

The interesting function here is `ping`. It walks the path hop by hop and then
walks the reply back, because a one-way path is the classic broken-lab result:
the learner adds a route towards the far subnet, the echo request arrives, and
nothing comes back because the far router has no route home. A simulator that
only checked the forward direction would call that success and teach the wrong
lesson.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

from .model import ConfigError, Device, Host, Interface, Router, Switch, normalise_ifname

__all__ = ["Lab", "PingResult", "TraceHop"]


@dataclass
class PingResult:
    ok: bool
    reason: str = ""
    path: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        arrow = " -> ".join(self.path) if self.path else "no path"
        return f"<Ping {'ok' if self.ok else 'failed'}: {arrow}{'' if self.ok else f' ({self.reason})'}>"


@dataclass
class TraceHop:
    number: int
    name: str
    ip: str


class Lab:
    """A topology: devices, the cables between them, and packet delivery."""

    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}

    # ---------- building ----------

    def add(self, device: Device) -> Device:
        self.devices[device.name] = device
        return device

    def router(self, name: str, *ifaces: str) -> Router:
        r = Router(name=name)
        for i in ifaces:
            r.add_interface(i)
        return self.add(r)  # type: ignore[return-value]

    def switch(self, name: str, *ifaces: str) -> Switch:
        s = Switch(name=name)
        for i in ifaces:
            iface = s.add_interface(i)
            iface.shutdown = False  # switch ports come up by default
        return self.add(s)  # type: ignore[return-value]

    def host(self, name: str, ip: str = "", mask: str = "", gateway: str = "") -> Host:
        h = Host(name=name, gateway=gateway or None)
        iface = h.add_interface("Ethernet0")
        iface.shutdown = False
        if ip:
            iface.ip, iface.mask = ip, mask or "255.255.255.0"
        return self.add(h)  # type: ignore[return-value]

    def link(self, a: str, b: str) -> None:
        """Cable two interfaces, each written as "device:interface"."""
        ia, ib = self._iface(a), self._iface(b)
        ia.link, ib.link = ib, ia

    def _iface(self, spec: str) -> Interface:
        dev_name, _, if_name = spec.partition(":")
        dev = self.device(dev_name)
        if_name = normalise_ifname(if_name)
        if if_name not in dev.interfaces:
            dev.add_interface(if_name)
            if isinstance(dev, (Switch, Host)):
                dev.interfaces[if_name].shutdown = False
        return dev.interfaces[if_name]

    def device(self, name: str) -> Device:
        if name not in self.devices:
            raise ConfigError(f"no device named {name!r} in this topology")
        return self.devices[name]

    # ---------- layer 2 ----------

    def segment(self, iface: Interface, vlan: int | None = None) -> set[Interface]:
        """
        Every interface in the same broadcast domain as `iface`.

        Walks outwards through cables, crossing switches only where the VLAN is
        allowed to pass. This is what makes "the ports are in different VLANs"
        produce a failed ping rather than a working one.
        """
        if vlan is None:
            vlan = iface.vlan if isinstance(iface.device, Switch) else 1
        seen: set[Interface] = set()
        stack = [(iface, vlan)]
        while stack:
            current, cur_vlan = stack.pop()
            if current in seen or not current.up:
                continue
            seen.add(current)
            peer = current.link
            if peer is None or peer.shutdown:
                continue
            seen.add(peer)
            if isinstance(peer.device, Switch):
                # A frame arriving on an access port belongs to that port's
                # VLAN; on a trunk it keeps the tag it already had.
                arriving = cur_vlan if peer.mode == "trunk" else peer.vlan
                if not peer.carries(arriving):
                    continue
                for other in peer.device.interfaces.values():
                    if other is not peer and other.up and other.carries(arriving):
                        stack.append((other, arriving))
        return seen

    def _reachable_l2(self, src: Interface, dst_ip: str) -> Interface | None:
        """Find the interface holding dst_ip in src's broadcast domain."""
        for cand in self.segment(src):
            if cand.ip == dst_ip and cand.up:
                return cand
        return None

    # ---------- layer 3 ----------

    def _egress(self, dev: Device, dst: str) -> tuple[Interface, str] | None:
        """Which interface leaves this device towards dst, and via which next hop."""
        if isinstance(dev, Host):
            iface = dev.iface
            if not iface.ip or not iface.network:
                return None
            if ipaddress.ip_address(dst) in iface.network:
                return iface, dst
            if not dev.gateway:
                return None
            return iface, dev.gateway

        if isinstance(dev, Router):
            if not dev.ip_routing:
                return None
            route = dev.lookup(dst)
            if route is None:
                return None
            if route.next_hop is None:  # connected
                iface = dev.interfaces[route.interface]  # type: ignore[index]
                return (iface, dst) if iface.up else None
            # Recursive lookup: the next hop has to be on a connected subnet.
            for iface in dev.interfaces.values():
                if iface.up and iface.network and ipaddress.ip_address(route.next_hop) in iface.network:
                    return iface, route.next_hop
            return None
        return None

    def _owner(self, ip: str) -> Device | None:
        for dev in self.devices.values():
            for iface in dev.interfaces.values():
                if iface.ip == ip:
                    return dev
        return None

    def _walk(self, src: Device, dst_ip: str, limit: int = 16) -> tuple[list[str], str]:
        """Follow the path from src towards dst_ip. Returns (path, failure reason)."""
        path = [src.name]
        current = src
        for _ in range(limit):
            for iface in current.interfaces.values():
                if iface.ip == dst_ip and iface.up:
                    return path, ""
            step = self._egress(current, dst_ip)
            if step is None:
                kind = "no route to" if isinstance(current, Router) else "no gateway for"
                return path, f"{current.hostname}: {kind} {dst_ip}"
            out_iface, next_hop = step
            if not out_iface.up:
                return path, f"{current.hostname}: {out_iface.name} is down"
            peer = self._reachable_l2(out_iface, next_hop)
            if peer is None:
                return path, f"{current.hostname}: {next_hop} is not reachable on {out_iface.name}"
            current = peer.device
            path.append(current.name)
            for iface in current.interfaces.values():
                if iface.ip == dst_ip and iface.up:
                    return path, ""
        return path, "TTL exceeded (routing loop)"

    def ping(self, src: str, dst: str) -> PingResult:
        """
        Ping by device name or IP. Both directions must work, as on real kit.
        """
        source = self.device(src) if src in self.devices else self._owner(src)
        if source is None:
            return PingResult(False, f"no device or address {src!r}")
        dst_ip = dst
        if dst in self.devices:
            target = self.device(dst)
            # Prefer a live address, but fall back to one that is merely down:
            # "the link is down" is a far more useful failure than "no address".
            addrs = target.addresses() or [i for i in target.interfaces.values() if i.ip]
            if not addrs:
                return PingResult(False, f"{dst} has no IP address configured")
            dst_ip = addrs[0].ip  # type: ignore[assignment]

        path, reason = self._walk(source, dst_ip)
        if reason:
            return PingResult(False, reason, path)

        # The reply. A route out with no route back is the classic half-done lab.
        target_dev = self._owner(dst_ip)
        src_addr = next((i.ip for i in source.addresses()), None)
        if target_dev is None or src_addr is None:
            return PingResult(False, "no source address to reply to", path)
        back, back_reason = self._walk(target_dev, src_addr)
        if back_reason:
            return PingResult(False, f"reply blocked - {back_reason}", path)
        return PingResult(True, "", path)

    def traceroute(self, src: str, dst: str) -> list[TraceHop]:
        source = self.device(src) if src in self.devices else self._owner(src)
        if source is None:
            return []
        dst_ip = dst
        if dst in self.devices:
            addrs = self.device(dst).addresses()
            dst_ip = addrs[0].ip if addrs else dst  # type: ignore[assignment]
        path, _ = self._walk(source, dst_ip)
        hops: list[TraceHop] = []
        for n, name in enumerate(path[1:], start=1):
            dev = self.device(name)
            addrs = dev.addresses()
            hops.append(TraceHop(n, name, addrs[0].ip if addrs else "*"))  # type: ignore[arg-type]
        return hops
