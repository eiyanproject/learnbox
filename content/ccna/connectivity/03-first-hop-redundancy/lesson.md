---
title: First hop redundancy with HSRP
summary: Two routers sharing one gateway address, so the PCs keep working when one of them dies.
order: 3
files: [r1.ios, r2.ios]
run: python lab.py
hints:
  - "R1 g0/0 is 192.168.1.1 and R2 g0/0 is 192.168.1.2; both share the virtual address 192.168.1.254, which is what PC1 already uses as its gateway."
  - "`standby 1 ip 192.168.1.254` on both routers, with the same group number. Different group numbers means two independent groups and no redundancy at all."
  - "Give R1 `standby 1 priority 110` so it wins; the default is 100. Add `standby 1 preempt` or R1 will not take the role back after it recovers."
  - "Both routers also need their uplink g0/1 addressed and a route to 10.10.10.0/24 via CORE, or the active router has nowhere to forward to."
---

A default gateway is a single address configured on every host. If the router
holding it fails, every host on that subnet is stranded — they have no way to
learn about the perfectly good second router next to it.

A **first hop redundancy protocol** fixes this by putting a *virtual* address
in front of two real ones. The hosts point at the virtual address and never
have to know which physical router is answering.

## HSRP

```
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 standby 1 ip 192.168.1.254
 standby 1 priority 110
 standby 1 preempt
```

- **The group number** (`1`) must match on both routers. It identifies the
  group; two routers in different groups are not redundant, they are two
  unrelated gateways.
- **The virtual IP** must match, and must not be either router's real address.
- **Priority** decides who is active — higher wins, default 100.
- **Preempt** decides whether a recovered router takes the role back. Without
  it, a router that reboots stays standby even though it has the higher
  priority, which surprises people every time.

The group also owns a virtual MAC address, which is the part that makes
failover invisible: the hosts' ARP entry for the gateway stays valid, so they
do not need to notice anything happened.

## Active and standby

One router is **active** and forwards; the other is **standby** and waits. They
exchange hellos, and if the standby stops hearing from the active it takes over
the virtual address.

Note what is *not* happening: there is no load sharing. The standby router's
link sits idle. (HSRP can be load-shared by running two groups with opposite
priorities and pointing half the hosts at each — a common exam wrinkle.)

## What HSRP does not do

Failover moves the *gateway*. It does not move anything upstream: CORE in this
lab has a static route pointing at R1, and that route does not notice R1's LAN
side failing. The hosts keep working and the return traffic still tries the
wrong path.

This is not a flaw in HSRP - it is the reason real designs run a routing
protocol alongside it, so the upstream path re-converges too. Worth knowing
before someone asks why the lab "still does not work" after a successful
failover.

## The other FHRPs

| | |
|---|---|
| HSRP | Cisco proprietary, active/standby |
| VRRP | Open standard, otherwise very similar |
| GLBP | Cisco, and actually load-balances across gateways |

The exam expects you to know which is which and that VRRP is the standard one.

## Your turn

The `redundant` topology: PC1 on a switch with two routers, both reaching CORE
and the server behind it. PC1's gateway is already set to 192.168.1.254 — an
address neither router owns yet.

Configure `r1.ios` and `r2.ios` so that:

- both routers are in HSRP group 1 for 192.168.1.254
- R1 is the active router, with priority 110 and preempt
- both have their uplink addressed and a route to the server's subnet

| Device | Interface | Address |
|---|---|---|
| R1 | g0/0 | 192.168.1.1/24 |
| R1 | g0/1 | 172.16.0.1/30 |
| R2 | g0/0 | 192.168.1.2/24 |
| R2 | g0/1 | 172.16.0.5/30 |

CORE already answers on 172.16.0.2 and 172.16.0.6, and owns 10.10.10.0/24.
