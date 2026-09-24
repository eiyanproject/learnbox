"""An IOS-shaped command interpreter over the model.

The point of typing real commands rather than calling Python is that the exam
tests the commands. So the modes are real modes: you cannot set an IP address
without entering interface configuration first, and the prompt changes to tell
you where you are. Commands not implemented are reported as IOS reports them,
with a caret under the offending token, rather than silently ignored - a
simulator that accepts anything teaches nothing.
"""

from __future__ import annotations

import ipaddress

from .lab import Lab
from .model import ConfigError, Host, Router, Switch, normalise_ifname
from .protocols import ACL, ACLEntry, DHCPPool, HSRPGroup, OSPF, wildcard_to_network

__all__ = ["Console", "apply_config"]

INVALID = "% Invalid input detected at '^' marker."
INCOMPLETE = "% Incomplete command."
NL = "\n"


class Console:
    """One device's CLI session. Feed it lines; collect output."""

    def __init__(self, lab: Lab, device_name: str) -> None:
        self.lab = lab
        self.dev = lab.device(device_name)
        self.mode = "user"  # user | enable | config | if | vlan
        self.target = None  # interface or vlan being configured

    # ---------- prompt ----------

    @property
    def prompt(self) -> str:
        h = self.dev.hostname
        return {
            "user": f"{h}>",
            "enable": f"{h}#",
            "config": f"{h}(config)#",
            "if": f"{h}(config-if)#",
            "vlan": f"{h}(config-vlan)#",
            "ospf": f"{h}(config-router)#",
            "acl": f"{h}(config-ext-nacl)#",
            "dhcp": f"{h}(config-dhcp)#",
        }[self.mode]

    # ---------- driving ----------

    def run(self, line: str) -> str:
        """Execute one line, returning what IOS would print (often nothing)."""
        text = line.split("!")[0].strip()
        if not text:
            return ""
        words = text.split()
        try:
            return self._dispatch(words) or ""
        except ConfigError as err:
            return f"% {err}"

    def run_all(self, text: str) -> list[str]:
        return [out for line in text.splitlines() if (out := self.run(line))]

    # ---------- dispatch ----------

    def _dispatch(self, w: list[str]) -> str | None:
        head = w[0].lower()

        # Navigation works from anywhere, as on real kit.
        if head in ("end", "exit"):
            return self._leave(head)
        if head == "enable":
            self.mode = "enable" if self.mode == "user" else self.mode
            return None
        if head == "disable":
            self.mode = "user"
            return None
        if head in ("show", "sh"):
            if self.mode == "user":
                self.mode = "user"  # show works in user mode for our subset
            return self._show(w[1:])
        if head == "ping":
            return self._ping(w[1:])
        if head == "traceroute":
            return self._traceroute(w[1:])

        if self.mode in ("user",):
            return self._invalid(w, 0)
        if self.mode == "enable":
            return self._enable_mode(w)
        if self.mode == "config":
            return self._config_mode(w)
        if self.mode == "if":
            return self._if_mode(w)
        if self.mode == "vlan":
            return self._vlan_mode(w)
        if self.mode == "ospf":
            return self._ospf_mode(w)
        if self.mode == "acl":
            return self._acl_mode(w)
        if self.mode == "dhcp":
            return self._dhcp_mode(w)
        return self._invalid(w, 0)

    def _leave(self, head: str) -> None:
        if head == "end":
            self.mode = "enable" if self.mode != "user" else "user"
            self.target = None
        else:  # exit
            self.mode = {
                "if": "config", "vlan": "config", "ospf": "config", "acl": "config",
                "dhcp": "config", "config": "enable", "enable": "user", "user": "user",
            }[self.mode]
            if self.mode == "config":
                self.target = None
        return None

    def _enable_mode(self, w: list[str]) -> str | None:
        if w[0].lower() in ("configure", "conf") and len(w) >= 2 and w[1].lower().startswith("t"):
            self.mode = "config"
            return None
        if w[0].lower() in ("configure", "conf"):
            return INCOMPLETE
        return self._invalid(w, 0)

    def _config_mode(self, w: list[str]) -> str | None:
        head = w[0].lower()
        if head == "hostname":
            if len(w) < 2:
                return INCOMPLETE
            self.dev.hostname = w[1]
            return None
        if head in ("interface", "int"):
            if len(w) < 2:
                return INCOMPLETE
            name = normalise_ifname(" ".join(w[1:]))
            if name not in self.dev.interfaces:
                # IOS creates subinterfaces and Vlan interfaces on demand.
                if name.startswith("Vlan") or "." in name or name.startswith("Loopback"):
                    iface = self.dev.add_interface(name)
                    iface.shutdown = False
                    if name.startswith("Vlan"):
                        # An SVI is the switch's own port in that VLAN, which is
                        # what lets it be the default gateway for the VLAN.
                        iface.vlan = int(name[4:])
                else:
                    return f"% Invalid interface {name}"
            self.target = self.dev.interfaces[name]
            self.mode = "if"
            return None
        if head == "vlan":
            if not isinstance(self.dev, Switch):
                return self._invalid(w, 0)
            if len(w) < 2:
                return INCOMPLETE
            self.dev.add_vlan(int(w[1]))
            self.target = int(w[1])
            self.mode = "vlan"
            return None
        if head == "ip" and len(w) >= 2 and w[1].lower() == "routing":
            # Also the command that turns a layer 2 switch into a layer 3 one.
            if hasattr(self.dev, "ip_routing"):
                self.dev.ip_routing = True
            return None
        if head == "no" and len(w) >= 3 and w[1].lower() == "ip" and w[2].lower() == "routing":
            if hasattr(self.dev, "ip_routing"):
                self.dev.ip_routing = False
            return None
        if head == "ip" and len(w) >= 2 and w[1].lower() == "route":
            return self._ip_route(w)
        if head == "router" and len(w) >= 3 and w[1].lower() == "ospf":
            self.dev.ospf = self.dev.ospf or OSPF(process=int(w[2]))
            self.mode = "ospf"
            return None
        if head == "access-list":
            return self._numbered_acl(w)
        if head == "ip" and len(w) >= 3 and w[1].lower() == "access-list":
            # ip access-list extended NAME
            if len(w) < 4:
                return INCOMPLETE
            name = w[3]
            self.dev.acls.setdefault(name, ACL(name))
            self.target = name
            self.mode = "acl"
            return None
        if head == "ip" and len(w) >= 3 and w[1].lower() == "nat":
            return self._ip_nat(w)
        if head == "ip" and len(w) >= 3 and w[1].lower() == "dhcp" and w[2].lower() == "pool":
            if len(w) < 4:
                return INCOMPLETE
            self.dev.dhcp_pools[w[3]] = DHCPPool(name=w[3])
            self.target = w[3]
            self.mode = "dhcp"
            return None
        if head == "ip" and len(w) >= 3 and w[1].lower() == "dhcp" and w[2].lower() == "excluded-address":
            return None  # recorded implicitly; nothing in the model leases yet
        return self._invalid(w, 0)

    # ---------- access lists ----------

    def _numbered_acl(self, w: list[str]) -> str | None:
        # access-list 10 permit 192.168.1.0 0.0.0.255   (standard: source only)
        if len(w) < 4:
            return INCOMPLETE
        name, action = w[1], w[2].lower()
        if action not in ("permit", "deny"):
            return self._invalid(w, 2)
        if w[3].lower() == "any":
            source = wildcard_to_network("0.0.0.0", "255.255.255.255")
        elif w[3].lower() == "host":
            if len(w) < 5:
                return INCOMPLETE
            source = wildcard_to_network(w[4], "0.0.0.0")
        else:
            if len(w) < 5:
                return INCOMPLETE
            source = wildcard_to_network(w[3], w[4])
        acl = self.dev.acls.setdefault(name, ACL(name))
        acl.entries.append(ACLEntry(action, "ip", source))
        return None

    def _acl_mode(self, w: list[str]) -> str | None:
        action = w[0].lower()
        if action not in ("permit", "deny"):
            return self._config_mode(w)
        if len(w) < 2:
            return INCOMPLETE
        protocol = w[1].lower()
        rest = w[2:]

        def take(tokens: list[str]):
            """Consume one address spec: any | host X | X wildcard."""
            if not tokens:
                return None, tokens
            if tokens[0].lower() == "any":
                return wildcard_to_network("0.0.0.0", "255.255.255.255"), tokens[1:]
            if tokens[0].lower() == "host":
                return wildcard_to_network(tokens[1], "0.0.0.0"), tokens[2:]
            return wildcard_to_network(tokens[0], tokens[1]), tokens[2:]

        try:
            source, rest = take(rest)
            destination, rest = take(rest)
        except (IndexError, ValueError):
            return INCOMPLETE
        if source is None or destination is None:
            return INCOMPLETE
        self.dev.acls[self.target].entries.append(ACLEntry(action, protocol, source, destination))
        return None

    # ---------- nat ----------

    def _ip_nat(self, w: list[str]) -> str | None:
        # ip nat inside source static 192.168.1.10 203.0.113.10
        # ip nat inside source list 1 interface g0/1 overload
        rest = [x.lower() for x in w[2:]]
        if len(rest) >= 3 and rest[1] == "source" and rest[2] == "static":
            if len(w) < 7:
                return INCOMPLETE
            self.dev.nat.static[w[5]] = w[6]
            return None
        if len(rest) >= 3 and rest[1] == "source" and rest[2] == "list":
            if len(w) < 8:
                return INCOMPLETE
            self.dev.nat.overload_acl = w[5]
            self.dev.nat.overload_interface = normalise_ifname(w[7])
            return None
        return self._invalid(w, 1)

    # ---------- ospf ----------

    def _ospf_mode(self, w: list[str]) -> str | None:
        head = w[0].lower()
        if head == "network":
            # network 10.0.0.0 0.0.0.255 area 0
            if len(w) < 5:
                return INCOMPLETE
            try:
                net = wildcard_to_network(w[1], w[2])
            except ValueError:
                return "% Invalid network or wildcard"
            self.dev.ospf.networks.append((net, int(w[4])))
            return None
        if head == "router-id":
            if len(w) < 2:
                return INCOMPLETE
            self.dev.ospf.router_id = w[1]
            return None
        if head == "passive-interface":
            return None
        return self._config_mode(w)

    # ---------- dhcp ----------

    def _dhcp_mode(self, w: list[str]) -> str | None:
        head = w[0].lower()
        pool = self.dev.dhcp_pools[self.target]
        if head == "network" and len(w) >= 3:
            pool.network = ipaddress.ip_network(f"{w[1]}/{w[2]}", strict=False)
            return None
        if head == "default-router" and len(w) >= 2:
            pool.default_router = w[1]
            return None
        if head == "dns-server" and len(w) >= 2:
            pool.dns_server = w[1]
            return None
        return self._config_mode(w)

    def _ip_route(self, w: list[str]) -> str | None:
        # ip route <network> <mask> <next-hop|interface>
        if len(w) < 5:
            return INCOMPLETE
        from .model import Route

        if not isinstance(self.dev, Router):
            return self._invalid(w, 0)
        try:
            net = ipaddress.ip_network(f"{w[2]}/{w[3]}", strict=False)
        except ValueError:
            return f"% Invalid network {w[2]} {w[3]}"
        hop = w[4]
        try:
            ipaddress.ip_address(hop)
            self.dev.static_routes.append(Route(net, hop, None, "S"))
        except ValueError:
            self.dev.static_routes.append(Route(net, None, normalise_ifname(hop), "S"))
        return None

    def _if_mode(self, w: list[str]) -> str | None:
        head = w[0].lower()
        iface = self.target
        if head == "no":
            return self._if_no(w[1:])
        if head == "shutdown":
            iface.shutdown = True
            return None
        if head == "description":
            iface.description = " ".join(w[1:])
            return None
        if head == "ip":
            if len(w) < 2:
                return INCOMPLETE
            if w[1].lower() == "address":
                if len(w) < 4:
                    return INCOMPLETE
                try:
                    ipaddress.ip_address(w[2])
                    ipaddress.ip_address(w[3])
                except ValueError:
                    return "% Invalid input detected"
                iface.ip, iface.mask = w[2], w[3]
                return None
            if w[1].lower() == "access-group":
                # ip access-group 10 in
                if len(w) < 4:
                    return INCOMPLETE
                if w[3].lower() == "in":
                    iface.acl_in = w[2]
                elif w[3].lower() == "out":
                    iface.acl_out = w[2]
                else:
                    return self._invalid(w, 3)
                return None
            # Exactly "ip nat inside" / "ip nat outside" marks this interface.
            # Anything longer is the global "ip nat inside source ..." command,
            # which is legal to type here and must not be mistaken for it.
            if w[1].lower() == "nat" and len(w) == 3:
                side = w[2].lower()
                if side not in ("inside", "outside"):
                    return self._invalid(w, 2)
                iface.nat_side = side
                return None
            return self._config_mode(w)
        if head == "encapsulation":
            # encapsulation dot1Q 10 - what makes a subinterface belong to a VLAN
            if len(w) < 3:
                return INCOMPLETE
            if w[1].lower() not in ("dot1q", "dot1Q".lower()):
                return self._invalid(w, 1)
            iface.encapsulation_vlan = int(w[2])
            iface.shutdown = False
            return None
        if head == "standby":
            # standby 1 ip 192.168.1.254 | standby 1 priority 110 | standby 1 preempt
            if len(w) < 3:
                return INCOMPLETE
            group = int(w[1])
            hsrp = iface.hsrp.setdefault(group, HSRPGroup(group=group, virtual_ip=""))
            what = w[2].lower()
            if what == "ip" and len(w) >= 4:
                hsrp.virtual_ip = w[3]
            elif what == "priority" and len(w) >= 4:
                hsrp.priority = int(w[3])
            elif what == "preempt":
                hsrp.preempt = True
            else:
                return self._invalid(w, 2)
            return None
        if head == "switchport":
            return self._switchport(w[1:])
        # Anything global typed here is accepted, as IOS accepts it: "interface
        # g0/1" straight after configuring g0/0 moves to the new interface
        # instead of erroring, and a config file written that way is normal.
        return self._config_mode(w)

    def _if_no(self, w: list[str]) -> str | None:
        if not w:
            return INCOMPLETE
        head = w[0].lower()
        if head == "shutdown":
            self.target.shutdown = False
            return None
        if head == "ip" and len(w) >= 2 and w[1].lower() == "address":
            self.target.ip = self.target.mask = None
            return None
        if head == "description":
            self.target.description = ""
            return None
        return self._invalid(["no", *w], 1)

    def _switchport(self, w: list[str]) -> str | None:
        iface = self.target
        if not w:
            return INCOMPLETE
        head = w[0].lower()
        if head == "mode":
            if len(w) < 2:
                return INCOMPLETE
            if w[1].lower() in ("access", "trunk"):
                iface.mode = w[1].lower()
                return None
            return self._invalid(["switchport", *w], 2)
        if head == "access":
            if len(w) < 3 or w[1].lower() != "vlan":
                return INCOMPLETE
            vid = int(w[2])
            if isinstance(self.dev, Switch) and vid not in self.dev.vlans:
                # IOS creates the VLAN implicitly and says so.
                self.dev.add_vlan(vid)
            iface.vlan = vid
            return None
        if head == "port-security":
            iface.port_security = True
            if len(w) >= 3 and w[1].lower() == "maximum":
                iface.port_security_max = int(w[2])
            elif len(w) >= 3 and w[1].lower() == "violation":
                iface.port_security_violation = w[2].lower()
            elif len(w) > 1 and w[1].lower() not in ("maximum", "violation"):
                return self._invalid(["switchport", *w], 1)
            return None
        if head == "trunk":
            if len(w) >= 4 and w[1].lower() == "allowed" and w[2].lower() == "vlan":
                iface.trunk_vlans = {int(v) for part in w[3].split(",") for v in _expand(part)}
                return None
            return INCOMPLETE
        return self._invalid(["switchport", *w], 1)

    def _vlan_mode(self, w: list[str]) -> str | None:
        if w[0].lower() == "name" and len(w) >= 2 and isinstance(self.dev, Switch):
            self.dev.vlans[self.target] = w[1]
            return None
        return self._config_mode(w)

    # ---------- show ----------

    def _show(self, w: list[str]) -> str:
        if not w:
            return INCOMPLETE
        what = " ".join(x.lower() for x in w)
        if what.startswith("ip int") or what.startswith("ip interface"):
            return self._show_ip_int_brief()
        if what.startswith("ip route"):
            return self._show_ip_route()
        if what.startswith("vlan"):
            return self._show_vlan()
        if what.startswith("ip ospf"):
            return self._show_ospf()
        if what.startswith("access-list") or what.startswith("ip access-list"):
            return self._show_acls()
        if what.startswith("ip nat"):
            return self._show_nat()
        if what.startswith("run"):
            return self.running_config()
        if what.startswith("interface"):
            return self._show_ip_int_brief()
        return INVALID

    def _show_ip_int_brief(self) -> str:
        rows = [f"{'Interface':<24}{'IP-Address':<17}{'OK?':<5}{'Status':<22}Protocol"]
        for iface in self.dev.interfaces.values():
            status = "administratively down" if iface.shutdown else ("up" if iface.link else "down")
            proto = "up" if iface.up else "down"
            rows.append(f"{iface.name:<24}{iface.ip or 'unassigned':<17}{'YES':<5}{status:<22}{proto}")
        return "\n".join(rows)

    def _show_ip_route(self) -> str:
        if not isinstance(self.dev, Router):
            return "% IP routing is not enabled on this device"
        head = "Codes: C - connected, S - static\n"
        lines = []
        for r in self.dev.routing_table():
            if r.source == "C":
                lines.append(f"C        {r.network} is directly connected, {r.interface}")
            elif r.next_hop:
                lines.append(f"S        {r.network} [1/0] via {r.next_hop}")
            else:
                lines.append(f"S        {r.network} is directly connected, {r.interface}")
        return head + ("\n".join(lines) if lines else "% No routes")

    def _show_vlan(self) -> str:
        if not isinstance(self.dev, Switch):
            return INVALID
        rows = [f"{'VLAN':<6}{'Name':<22}{'Status':<10}Ports"]
        for vid, name in sorted(self.dev.vlans.items()):
            ports = ", ".join(i.name for i in self.dev.interfaces.values() if i.mode == "access" and i.vlan == vid)
            rows.append(f"{vid:<6}{name:<22}{'active':<10}{ports}")
        return "\n".join(rows)

    def _show_ospf(self) -> str:
        ospf = getattr(self.dev, "ospf", None)
        if not ospf:
            return "% OSPF is not running on this device"
        self.lab.converge_ospf()
        lines = [f"Routing Process \"ospf {ospf.process}\""]
        for net, area in ospf.networks:
            lines.append(f"  network {net} area {area}")
        learned = getattr(self.dev, "ospf_routes", [])
        lines.append(f"  {len(learned)} route(s) learned")
        for r in learned:
            lines.append(f"O        {r.network} [110/1] via {r.next_hop}")
        return NL.join(lines)

    def _show_acls(self) -> str:
        acls = getattr(self.dev, "acls", {})
        if not acls:
            return "% No access lists configured"
        lines = []
        for name, acl in acls.items():
            lines.append(f"Access list {name}")
            for e in acl.entries:
                dst = f" -> {e.destination}" if e.destination is not None else ""
                lines.append(f"    {e.action} {e.protocol} {e.source}{dst}")
        return NL.join(lines)

    def _show_nat(self) -> str:
        nat = getattr(self.dev, "nat", None)
        if not nat or (not nat.static and not nat.overload_interface):
            return "% No NAT configured"
        lines = ["Pro  Inside global     Inside local"]
        for local, glob in nat.static.items():
            lines.append(f"---  {glob:<18}{local}")
        if nat.overload_interface:
            lines.append(f"PAT  via {nat.overload_interface} (list {nat.overload_acl})")
        return NL.join(lines)

    def running_config(self) -> str:
        out = [f"hostname {self.dev.hostname}", "!"]
        for iface in self.dev.interfaces.values():
            out.append(f"interface {iface.name}")
            if iface.description:
                out.append(f" description {iface.description}")
            if iface.ip:
                out.append(f" ip address {iface.ip} {iface.mask}")
            if isinstance(self.dev, Switch):
                out.append(f" switchport mode {iface.mode}")
                if iface.mode == "access" and iface.vlan != 1:
                    out.append(f" switchport access vlan {iface.vlan}")
            out.append(" shutdown" if iface.shutdown else " no shutdown")
            out.append("!")
        if isinstance(self.dev, Router):
            for r in self.dev.static_routes:
                target = r.next_hop or r.interface
                out.append(f"ip route {r.network.network_address} {r.network.netmask} {target}")
        return "\n".join(out)

    # ---------- reachability ----------

    def _ping(self, w: list[str]) -> str:
        if not w:
            return INCOMPLETE
        res = self.lab.ping(self.dev.name, w[0])
        if res.ok:
            return "!!!!!\nSuccess rate is 100 percent (5/5)"
        return f".....\nSuccess rate is 0 percent (0/5)\n% {res.reason}"

    def _traceroute(self, w: list[str]) -> str:
        if not w:
            return INCOMPLETE
        hops = self.lab.traceroute(self.dev.name, w[0])
        if not hops:
            return "% no path"
        return "\n".join(f"  {h.number}  {h.ip}  [{h.name}]" for h in hops)

    # ---------- errors ----------

    def _invalid(self, w: list[str], at: int) -> str:
        """IOS points a caret at the first token it did not understand."""
        line = " ".join(w)
        col = sum(len(x) + 1 for x in w[:at])
        return f"{' ' * col}^\n{INVALID}"


def _expand(part: str) -> list[int]:
    if "-" in part:
        lo, hi = part.split("-", 1)
        return list(range(int(lo), int(hi) + 1))
    return [int(part)]


def apply_config(lab: Lab, device: str, text: str) -> list[str]:
    """
    Apply a config file to a device, returning the lines IOS complained about.

    Lessons grade on an empty list plus a working ping: a config that IOS would
    have rejected should not pass just because the network happens to work.
    """
    console = Console(lab, device)
    console.mode = "enable"
    console.run("configure terminal")
    errors: list[str] = []
    for raw in text.splitlines():
        line = raw.split("!")[0].strip()
        if not line:
            continue
        out = console.run(line)
        if out and ("Invalid" in out or "Incomplete" in out or out.startswith("%")):
            errors.append(f"{raw.strip()}  ->  {out.splitlines()[-1]}")
    return errors
