---
title: Router on a stick
summary: One physical link, one subinterface per VLAN, and the encapsulation command that ties them together.
order: 3
files: [sw1.ios, r1.ios]
run: python lab.py
hints:
  - "The switch side is a trunk: Fa0/1 access VLAN 10, Fa0/2 access VLAN 20, and Gi0/1 `switchport mode trunk` facing the router."
  - "On the router, bring the PHYSICAL interface up first (`interface GigabitEthernet0/0` then `no shutdown`). A subinterface whose parent is shut is also down."
  - "Subinterfaces are named after the VLAN by convention: `interface GigabitEthernet0/0.10`, then `encapsulation dot1Q 10`, then the address."
  - "The address on each subinterface is the gateway the PCs already point at: 10.0.10.1 for VLAN 10 and 10.0.20.1 for VLAN 20."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **router on a stick** | one router link carrying every VLAN, split into subinterfaces |
| **subinterface** | a logical interface on a physical one, such as `Gi0/0.10` |
| **encapsulation** | which VLAN tag a subinterface answers to |
| **subnet** | a range of addresses on one network, such as 10.0.10.0/24 |
| **gateway** (default gateway) | the router address a host sends other-subnet traffic to |
| **connected route** | a route to a subnet the router has an interface in; no static route needed |
| **bottleneck** | the part that limits throughput; here the single link, crossed twice |
| **layer 3 switch** | a switch that routes in hardware (next lesson) |
| **`shutdown`** | an interface turned off; router interfaces start this way |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | applies your configuration to the lab topology and runs the pings |

### IOS commands

| Command | What it does |
|---|---|
| `interface GigabitEthernet0/0` then `no shutdown` | brings up the physical interface |
| `interface GigabitEthernet0/0.10` | creates subinterface 10 |
| `encapsulation dot1Q 10` | binds it to VLAN 10 |
| `ip address 10.0.10.1 255.255.255.0` | gives it the gateway address |
| `switchport mode trunk` | the switch side of the link |

---

VLANs cannot talk to each other without a router. But buying one router
interface per VLAN does not scale, and most of them would sit nearly idle.

**Router on a stick** uses one physical link carrying tagged frames for every
VLAN, and splits it logically on the router into one **subinterface** per VLAN.

## The two halves

The switch side is just a trunk:

```
interface GigabitEthernet0/1
 switchport mode trunk
```

The router side creates a subinterface per VLAN and tells each one which tag it
answers to:

```
interface GigabitEthernet0/0
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
```

Three things to notice:

- **The number after the dot is a label, not the VLAN.** `Gi0/0.10` could carry
  VLAN 99 if you said `encapsulation dot1Q 99`. Matching them is a convention
  that exists to keep you sane, and every real network follows it.
- **`encapsulation dot1Q <vlan>` is what actually binds the VLAN.** Without it
  a subinterface has an address and receives nothing.
- **The physical interface needs `no shutdown`.** It usually has no address at
  all — it is just the pipe — but if it is down, every subinterface on it is
  down too.

## Where the traffic goes

PC1 sends to PC2's address, sees it is in another subnet, and hands the frame
to its gateway 10.0.10.1. The switch tags it VLAN 10 and sends it up the trunk.
The router receives it on Gi0/0.10, routes it — both subnets are connected
routes, so no static route is needed — and sends it back down the same trunk
tagged VLAN 20.

The frame crosses the same cable twice. That is why the link is the bottleneck
and why a layer 3 switch, which does this in hardware, is the usual answer in
a real building.

## Your turn

The `router-on-a-stick` topology: PC1 in VLAN 10, PC2 in VLAN 20, one switch,
one router link.

Configure `sw1.ios` (access ports and the trunk) and `r1.ios` (the physical
interface and one subinterface per VLAN) so PC1 and PC2 can reach each other.
