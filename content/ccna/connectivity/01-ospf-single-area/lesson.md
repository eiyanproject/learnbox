---
title: OSPF in one area
summary: Routers telling each other what they know, instead of you telling each of them - and the network statement that decides what gets shared.
order: 1
files: [r1.ios, r2.ios]
run: python lab.py
hints:
  - "Address the interfaces exactly as in the static-routes lesson: R1 g0/0 192.168.1.1/24 and g0/1 10.0.0.1/30; R2 g0/0 192.168.3.1/24 and g0/1 10.0.0.2/30."
  - "`router ospf 1` enters OSPF configuration. The 1 is a process id, local to the device - it does NOT have to match between routers."
  - "`network 192.168.1.0 0.0.0.255 area 0` uses a WILDCARD mask, the inverse of a subnet mask. /24 is 0.0.0.255; the /30 link is 0.0.0.3."
  - "Both the LAN and the link need network statements on each router. Advertising only the link means the far LAN is never learned."
---

Static routes work until the fourth router. Every new subnet means editing
every other device, and forgetting one is invisible until something breaks in
one direction only.

OSPF replaces that with routers telling each other what they are connected to.

## Two commands

```
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
```

The `1` is a **process id**. It is local to the router and does not need to
match anywhere else — two routers with process 1 and process 5 will happily
become neighbours. The exam asks about this.

The `area 0` does have to match. Area 0 is the backbone; in a single-area
design everything is in it.

## The network statement does two jobs

This is the part worth slowing down for. `network 192.168.1.0 0.0.0.255 area 0`
means: *every interface of mine with an address inside 192.168.1.0/24 should
participate in OSPF*. Participating means two separate things:

1. **Advertise that subnet** to the neighbours.
2. **Look for neighbours** out of that interface.

So a link with no network statement forms no adjacency — the routers are
cabled together and never speak. And a LAN with no network statement is never
advertised, so everyone else's routing table has a hole in exactly one place.

## Wildcard masks

The mask is inverted. Where a subnet mask has 255, a wildcard has 0:

| Subnet mask | Wildcard | Prefix |
|---|---|---|
| 255.255.255.0 | 0.0.0.255 | /24 |
| 255.255.255.252 | 0.0.0.3 | /30 |
| 255.255.0.0 | 0.0.255.255 | /16 |
| 255.255.255.255 | 0.0.0.0 | a single host |

Zero means "these bits must match"; one means "don't care". Subtracting each
octet from 255 converts between them.

## Reading the result

Learned routes appear with an `O`:

```
O        192.168.3.0/24 [110/2] via 10.0.0.2
```

`110` is OSPF's administrative distance. A static route's distance is 1, so a
static route for the same prefix always wins — which is how you override OSPF,
and how you accidentally break it.

## Your turn

Same `two-routers` topology as the static routing lesson, but this time neither
router gets a single `ip route`. Configure addresses and OSPF on both so PC1
and PC2 can reach each other.
