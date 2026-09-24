---
title: Layer 3 switching with SVIs
summary: Giving a switch its own interface in each VLAN, turning on ip routing, and retiring the router on a stick.
order: 4
files: [sw1.ios]
run: python lab.py
hints:
  - "`ip routing` is the command that makes the switch route. Without it the SVIs exist, have addresses, answer pings - and do not forward between VLANs."
  - "An SVI is created by `interface Vlan10`. The number is the VLAN; there is no encapsulation command, because the switch already knows which ports are in which VLAN."
  - "Put the ports in their VLANs as usual: Fa0/1 and Fa0/3 in VLAN 10, Fa0/2 in VLAN 20."
  - "The SVI address is the gateway the PCs point at: 10.0.10.1 for Vlan10, 10.0.20.1 for Vlan20."
---

Router on a stick works and it has one obvious flaw: every packet between two
VLANs crosses the same cable twice. A layer 3 switch removes the cable
entirely by doing the routing itself.

## The SVI

A **switched virtual interface** is the switch's own interface inside a VLAN:

```
interface Vlan10
 ip address 10.0.10.1 255.255.255.0
```

There is no `encapsulation` command and no physical port. The switch already
knows which ports are in VLAN 10, and the SVI is simply its own presence in
that broadcast domain. Give it an address and it becomes the default gateway
for everything in the VLAN.

An SVI is up when the VLAN exists and at least one port in it is up. It does
not need a cable of its own, which is why `show ip interface brief` shows it
differently from a physical port.

## The command people forget

```
ip routing
```

A layer 2 switch with SVIs will happily answer pings to those addresses and
still refuse to forward a packet from one VLAN to another. Everything looks
configured; nothing works. `ip routing` is the switch equivalent of the
router's default behaviour, and on a switch it is **off** by default.

This is worth internalising because the symptom is so misleading: the gateway
responds, so the learner concludes the gateway is fine and goes looking at the
PCs.

## Which to use

| | Router on a stick | Layer 3 switch |
|---|---|---|
| Inter-VLAN traffic | Crosses the trunk twice | Stays inside the switch |
| Speed | Router CPU / one link | Switching hardware |
| Cost | Cheaper hardware | More expensive switch |
| Typical use | Small sites, labs, exams | Any real campus network |

Both are examinable; the second is what you would actually deploy.

## Your turn

The `l3-switch` topology: PC1 and PC3 in VLAN 10, PC2 in VLAN 20, all on one
switch and no router anywhere.

In `sw1.ios`:

- create VLANs 10 and 20 and put Fa0/1 and Fa0/3 in 10, Fa0/2 in 20
- create `Vlan10` with 10.0.10.1/24 and `Vlan20` with 10.0.20.1/24
- turn on `ip routing`

PC1 must reach PC2 (different VLANs, via the switch) and PC3 (same VLAN,
switched directly).
