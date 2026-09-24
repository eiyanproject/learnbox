---
title: Routing between two subnets
summary: Why two hosts on different subnets cannot talk without a router, what a default gateway is for, and the connected routes you get for free.
order: 2
files: [r1.ios]
run: python lab.py
hints:
  - "Both interfaces this time: GigabitEthernet0/0 for 192.168.1.0/24 and GigabitEthernet0/1 for 192.168.2.0/24. Each needs an address and `no shutdown`."
  - "The address you give an interface must be the one the PCs already use as their gateway: 192.168.1.1 on one side, 192.168.2.1 on the other."
  - "You do not write any `ip route` commands here. A router learns a route to every subnet it has an address on, automatically - those are the C lines in `show ip route`."
  - "If one direction works and the other does not, check `show ip interface brief` on both interfaces: the usual cause is a missing `no shutdown` on the second one."
---

PC1 is on 192.168.1.0/24. PC2 is on 192.168.2.0/24. They are three metres
apart and they cannot talk, because a host can only deliver a frame directly
to something inside its own subnet. Everything else it hands to its **default
gateway** and hopes.

## How a host decides

Before sending anything, a host does one calculation:

```
my address    192.168.1.10
my mask       255.255.255.0   ->  my subnet is 192.168.1.0 - 192.168.1.255
destination   192.168.2.10    ->  outside my subnet
```

Inside its subnet, it sends the frame straight to the destination. Outside, it
sends the frame to the **gateway's MAC address** but with the destination's
**IP address** still in the packet. That split — layer 2 addressed to the next
hop, layer 3 addressed to the final target — is the single most important idea
in routing, and it repeats at every hop.

A host with no gateway configured and a non-local destination simply fails.
There is nowhere to send it.

## What the router gets for free

Give an interface an address and the router immediately knows one route:

```
R1# show ip route
Codes: C - connected, S - static
C        192.168.1.0/24 is directly connected, GigabitEthernet0/0
C        192.168.2.0/24 is directly connected, GigabitEthernet0/1
```

`C` is **connected**: "I have an interface in this subnet, I can deliver to it
directly." You do not configure these and you cannot delete them; they appear
when the interface has an address and is up, and vanish when it goes down.

Two connected routes is all this topology needs. A router joining two subnets
that both terminate on it needs no `ip route` at all — which is worth knowing
because the exam likes to offer you a static route you do not need.

## Reading failure

When a ping fails, the question is always *which direction*. A useful habit:

- ping the router's near interface from the PC — if that fails, the problem is
  local: address, mask, or the interface being down
- ping the router's far interface — if that works but the far PC does not, the
  problem is on the far side
- `show ip route` on the router — if the destination subnet is not listed, the
  router does not know where to send it, whatever the PCs are doing

## Your turn

Same `one-router` topology. In `r1.ios`, configure **both** interfaces so PC1
and PC2 can reach each other:

| Interface | Address | Mask |
|---|---|---|
| GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |
| GigabitEthernet0/1 | 192.168.2.1 | 255.255.255.0 |

Both must be up. No static routes are needed or wanted.
