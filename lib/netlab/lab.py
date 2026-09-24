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

    # ---------- routing protocols ----------

    def _l3_devices(self) -> list[Device]:
        """Everything that can route: routers, and switches with ip routing on."""
        return [
            d
            for d in self.devices.values()
            if isinstance(d, Router) or (isinstance(d, Switch) and getattr(d, "ip_routing", False))
        ]

    def converge_ospf(self) -> None:
        """
        Fill in every OSPF speaker's learned routes.

        Real OSPF floods LSAs and each router runs Dijkstra over the result.
        The outcome for a single area is the same as running Dijkstra here over
        the graph of OSPF-enabled links, which is what a lesson can assert on.
        A router only advertises, and only forms adjacencies over, interfaces
        covered by a `network` statement - so a missing statement leaves a
        subnet unreachable, exactly as it does on real kit.
        """
        speakers = [d for d in self._l3_devices() if getattr(d, "ospf", None)]
        for dev in speakers:
            dev.ospf_routes = []
        if not speakers:
            return

        from .model import Route

        def enabled(dev: Device, iface: Interface) -> bool:
            return bool(iface.ip and iface.up and dev.ospf and dev.ospf.covers(iface.ip))

        # Dijkstra from each speaker across OSPF-enabled interfaces.
        for me in speakers:
            best: dict[str, tuple[int, str | None, str | None]] = {}  # network -> (cost, next hop, out iface)
            frontier: list[tuple[int, Device, str | None, str | None]] = [(0, me, None, None)]
            visited: set[str] = set()
            while frontier:
                frontier.sort(key=lambda t: t[0])
                cost, dev, via, out = frontier.pop(0)
                if dev.name in visited:
                    continue
                visited.add(dev.name)
                for iface in dev.interfaces.values():
                    if not enabled(dev, iface) or not iface.network:
                        continue
                    key = str(iface.network)
                    if dev is not me and (key not in best or cost < best[key][0]):
                        best[key] = (cost, via, out)
                    # Cross to every OSPF neighbour on this subnet.
                    for peer in self.segment(iface):
                        neighbour = peer.device
                        if neighbour is dev or neighbour.name in visited:
                            continue
                        if not getattr(neighbour, "ospf", None) or not enabled(neighbour, peer):
                            continue
                        next_via = peer.ip if dev is me else via
                        next_out = iface.name if dev is me else out
                        frontier.append((cost + 1, neighbour, next_via, next_out))
            connected = {
                str(i.network) for i in me.interfaces.values() if i.ip and i.up and i.network
            }
            for net_str, (_, via, out) in best.items():
                if via is None or net_str in connected:
                    continue  # a connected route always wins; do not shadow it
                me.ospf_routes.append(Route(ipaddress.ip_network(net_str), via, out, "O"))

    # ---------- filtering and translation ----------

    def _acl_allows(self, dev: Device, iface: Interface, direction: str, src: str, dst: str) -> tuple[bool, str]:
        name = iface.acl_in if direction == "in" else iface.acl_out
        if not name:
            return True, ""
        acl = getattr(dev, "acls", {}).get(name)
        if acl is None:
            return True, ""  # applied but not defined: IOS permits in that case
        if acl.permits(src, dst):
            return True, ""
        return False, f"{dev.hostname}: access list {name} denied {src} -> {dst} {direction}bound on {iface.name}"

    def _nat_source(self, dev: Device, out_iface: Interface, src: str) -> str:
        """Rewrite the source if this packet is leaving an inside interface for an outside one."""
        nat = getattr(dev, "nat", None)
        if not nat or out_iface.nat_side != "outside":
            return src
        return nat.translate(src, out_iface.ip)

    # ---------- layer 2 ----------

    def segment(self, iface: Interface, vlan: int | None = None) -> set[Interface]:
        """
        Every interface in the same broadcast domain as `iface`.

        Walks outwards through cables, crossing switches only where the VLAN is
        allowed to pass. This is what makes "the ports are in different VLANs"
        produce a failed ping rather than a working one.
        """
        if vlan is None:
            if iface.encapsulation_vlan is not None:
                vlan = iface.encapsulation_vlan
            elif isinstance(iface.device, Switch):
                vlan = iface.vlan
            else:
                vlan = 1
        seen: set[Interface] = set()
        # A subinterface rides its parent's cable, tagged with its own VLAN.
        start = iface.parent or iface
        if start.virtual and isinstance(start.device, Switch):
            # An SVI has no cable: its broadcast domain is every port on the
            # switch that is in its VLAN.
            seen.add(start)
            vlan = start.vlan
            stack = [
                (port, vlan)
                for port in start.device.interfaces.values()
                if not port.virtual and port.up and port.carries(vlan)
            ]
        else:
            stack = [(start, vlan)]
        while stack:
            current, cur_vlan = stack.pop()
            if current in seen or not current.up:
                continue
            seen.add(current)
            peer = current.link
            if peer is None or peer.shutdown:
                continue
            seen.add(peer)
            # Router-on-a-stick: the tagged frame is answered by the
            # subinterface whose encapsulation matches, not by the physical port.
            for sub in peer.device.interfaces.values():
                if sub.parent is peer and sub.encapsulation_vlan == cur_vlan and sub.up:
                    seen.add(sub)
            if isinstance(peer.device, Switch) and not peer.device.interfaces:
                pass
            if isinstance(peer.device, Switch):
                # A frame arriving on an access port belongs to that port's
                # VLAN; on a trunk it keeps the tag it already had.
                arriving = cur_vlan if peer.mode == "trunk" else peer.vlan
                if not peer.carries(arriving):
                    continue
                for other in peer.device.interfaces.values():
                    if other is peer or not other.up:
                        continue
                    if other.virtual:
                        # The switch's own SVI in this VLAN: reachable here,
                        # but it is an endpoint, not a way through to elsewhere.
                        if other.vlan == arriving:
                            seen.add(other)
                        continue
                    if other.carries(arriving):
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

        if isinstance(dev, Router) or (isinstance(dev, Switch) and dev.ip_routing):
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

    def _walk(self, src: Device, dst_ip: str, limit: int = 16, src_ip: str | None = None) -> tuple[list[str], str, str]:
        """Follow the path from src towards dst_ip. Returns (path, failure reason)."""
        path = [src.name]
        current = src
        if src_ip is None:
            addrs = src.addresses()
            src_ip = addrs[0].ip if addrs else ""
        for _ in range(limit):
            for iface in current.interfaces.values():
                if iface.ip == dst_ip and iface.up:
                    return path, "", src_ip or ""
            step = self._egress(current, dst_ip)
            if step is None:
                kind = "no route to" if isinstance(current, Router) else "no gateway for"
                return path, f"{current.hostname}: {kind} {dst_ip}", src_ip or ""
            out_iface, next_hop = step
            if not out_iface.up:
                return path, f"{current.hostname}: {out_iface.name} is down", src_ip or ""
            ok, why = self._acl_allows(current, out_iface, "out", src_ip, dst_ip)
            if not ok:
                return path, why, src_ip or ""
            # Source translation happens on the way out of the inside network.
            src_ip = self._nat_source(current, out_iface, src_ip)
            peer = self._reachable_l2(out_iface, next_hop)
            if peer is None:
                return path, f"{current.hostname}: {next_hop} is not reachable on {out_iface.name}", src_ip or ""
            ok, why = self._acl_allows(peer.device, peer, "in", src_ip, dst_ip)
            if not ok:
                return path + [peer.device.name], why, src_ip or ""
            current = peer.device
            path.append(current.name)
            for iface in current.interfaces.values():
                if iface.ip == dst_ip and iface.up:
                    return path, "", src_ip or ""
        return path, "TTL exceeded (routing loop)", src_ip or ""

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

        self.converge_ospf()
        src_addr = next((i.ip for i in source.addresses()), None)
        path, reason, seen_as = self._walk(source, dst_ip, src_ip=src_addr)
        if reason:
            return PingResult(False, reason, path)

        # The reply. A route out with no route back is the classic half-done lab.
        target_dev = self._owner(dst_ip)
        if target_dev is None or src_addr is None:
            return PingResult(False, "no source address to reply to", path)
        # The reply comes from the address the request was last seen using,
        # which is the translated one when NAT is in the path.
        # The far end replies to whatever source address reached it, which
        # after NAT is the translated one, not the host's own.
        back, back_reason, _ = self._walk(target_dev, seen_as or src_addr, src_ip=dst_ip)
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
        self.converge_ospf()
        path, _, _ = self._walk(source, dst_ip)
        hops: list[TraceHop] = []
        for n, name in enumerate(path[1:], start=1):
            dev = self.device(name)
            addrs = dev.addresses()
            hops.append(TraceHop(n, name, addrs[0].ip if addrs else "*"))  # type: ignore[arg-type]
        return hops
