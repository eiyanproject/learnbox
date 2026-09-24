---
title: How a router chooses
summary: Longest prefix first, then administrative distance, then metric - the order that decides every forwarding decision.
order: 2
files: [routing.py]
run: python -i routing.py
hints:
  - "`best_route` compares prefix length FIRST. A /32 beats a /24 beats a /0, whatever the protocol or metric behind it."
  - "Only when two routes have the same prefix length does administrative distance decide: connected 0, static 1, OSPF 110, RIP 120."
  - "Metric is the last tiebreak, and only between routes from the same protocol - comparing an OSPF cost with a RIP hop count is meaningless."
  - "`ipaddress.ip_network(cidr)` gives `.prefixlen`, and `ipaddress.ip_address(ip) in network` is the membership test."
---

Every packet a router forwards goes through the same decision, in a fixed
order. Knowing the order answers most routing questions on the exam without
any configuration at all.

## 1. Longest prefix wins

The router finds every route whose network contains the destination, and picks
the **most specific** one — the longest prefix.

```
192.168.1.0/24    via A
192.168.1.0/26    via B
0.0.0.0/0         via C
```

A packet for 192.168.1.10 goes via **B**. Not because B is better, faster or
newer, but because /26 is longer than /24. The default route 0.0.0.0/0 is the
shortest possible prefix, which is exactly why it is the last resort.

This rule beats everything below it. A /26 learned by RIP beats a /24 that is
directly connected.

## 2. Administrative distance breaks ties between protocols

If two routes have the same prefix length, the router trusts the source with
the lowest distance:

| Source | Distance |
|---|---|
| Connected | 0 |
| Static | 1 |
| eBGP | 20 |
| OSPF | 110 |
| RIP | 120 |
| Unusable | 255 |

Distance is "how much do I believe this", not "how good is the path". It is
why adding a static route silently overrides OSPF for that prefix, and why
`255` means the route is never used.

## 3. Metric breaks ties within a protocol

Same prefix, same protocol, two paths: the lower metric wins. OSPF uses cost
(derived from bandwidth), RIP uses hop count. Comparing metrics *across*
protocols is meaningless, which is why distance is checked first.

## Your turn

In `routing.py`, model the decision:

- `matching(routes, ip)`: every route whose network contains `ip`. A route is a
  dict with `network` (a CIDR string), `distance` and `metric`.
- `best_route(routes, ip)`: the one the router would use, applying the three
  rules in order. Return `None` if nothing matches.
- `is_default(route)`: whether a route is the default route
- `beats(a, b)`: whether route `a` would be preferred over route `b` for a
  destination both of them match
