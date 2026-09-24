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

__all__ = ["Console", "apply_config"]

INVALID = "% Invalid input detected at '^' marker."
INCOMPLETE = "% Incomplete command."


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
        return self._invalid(w, 0)

    def _leave(self, head: str) -> None:
        if head == "end":
            self.mode = "enable" if self.mode != "user" else "user"
            self.target = None
        else:  # exit
            self.mode = {"if": "config", "vlan": "config", "config": "enable", "enable": "user", "user": "user"}[self.mode]
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
            if isinstance(self.dev, Router):
                self.dev.ip_routing = True
            return None
        if head == "no" and len(w) >= 3 and w[1].lower() == "ip" and w[2].lower() == "routing":
            if isinstance(self.dev, Router):
                self.dev.ip_routing = False
            return None
        if head == "ip" and len(w) >= 2 and w[1].lower() == "route":
            return self._ip_route(w)
        return self._invalid(w, 0)

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
            return self._config_mode(w)
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
