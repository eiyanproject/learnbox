---
title: Trunks between switches
summary: Carrying several VLANs down one cable with 802.1Q tags, and what happens to the VLAN that is not tagged.
order: 2
files: [sw1.ios, sw2.ios]
run: python lab.py
hints:
  - "Access ports first: Fa0/1 in VLAN 10 and Fa0/2 in VLAN 20 on both switches, exactly as in the previous lesson."
  - "The link between the switches is GigabitEthernet0/1 on each. It needs `switchport mode trunk` at BOTH ends - a trunk facing an access port does not work."
  - "`switchport trunk allowed vlan 10,20` restricts which VLANs cross. Leaving it out allows them all, which is fine here but is not what you want in production."
  - "If PC1 reaches PC3 but PC2 cannot reach PC4, check you configured both VLANs on both switches - a VLAN that exists on one switch only has nowhere to go."
---

One cable between two switches has to carry every VLAN that spans them. An
access port cannot: it carries one VLAN and sends frames untagged, so the far
switch has no way to tell which VLAN a frame belonged to.

A **trunk** solves this by tagging. Each frame leaving a trunk carries a small
802.1Q header naming its VLAN; the switch at the other end reads the tag, strips
it, and puts the frame into the matching VLAN.

## Configuring one

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

Both ends must be trunks. A trunk facing an access port is one of the most
common lab faults: the access side drops tagged frames it does not understand,
and the symptom is that one VLAN works (the untagged one) and the others do not.

## The native VLAN

One VLAN on every trunk travels **untagged** — the native VLAN, VLAN 1 by
default. It exists for compatibility with devices that do not understand tags.

Two consequences worth remembering:

- The native VLAN must match at both ends. If one switch calls VLAN 1 native
  and the other calls VLAN 99 native, untagged frames silently cross between
  those two VLANs. That is a security hole, not just a misconfiguration.
- Because the native VLAN is untagged, an attacker who can inject tagged frames
  on an access port in the native VLAN may be able to reach another VLAN. This
  is why the advice is to make the native VLAN an unused one.

## Pruning

`switchport trunk allowed vlan 10,20` says only those VLANs may cross. Anything
else is dropped at the trunk. Restricting this is worth doing: it limits
broadcast traffic, and it means adding a VLAN somewhere does not automatically
extend it everywhere.

## Your turn

The `two-switches` topology: PC1 and PC3 should end up in VLAN 10, PC2 and PC4
in VLAN 20, with the switches joined by GigabitEthernet0/1.

| Switch | Port | VLAN |
|---|---|---|
| SW1 | Fa0/1 (PC1) | 10 |
| SW1 | Fa0/2 (PC2) | 20 |
| SW2 | Fa0/1 (PC3) | 10 |
| SW2 | Fa0/2 (PC4) | 20 |

Configure both switches so PC1 reaches PC3 and PC2 reaches PC4, while VLAN 10
and VLAN 20 stay separate.
