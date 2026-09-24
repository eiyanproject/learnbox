---
title: VLANs and access ports
summary: Splitting one switch into separate broadcast domains, and why two PCs on the same switch can stop being able to talk.
order: 1
files: [sw1.ios]
run: python lab.py
hints:
  - "Create the VLAN first (`vlan 10`, then `vlan 20`), then put each port in one. A VLAN that does not exist is created implicitly when you assign it, but making it explicit is the habit the exam wants."
  - "Two commands per port: `switchport mode access` fixes the port as an access port, `switchport access vlan 10` says which VLAN."
  - "Fa0/1 and Fa0/3 go in VLAN 10; Fa0/2 and Fa0/4 go in VLAN 20."
  - "`show vlan brief` lists which ports ended up where - the quickest way to spot a port you forgot."
---

A switch out of the box is one flat broadcast domain: every port can talk to
every other port. A VLAN divides that switch into several, and the division is
absolute — traffic cannot cross from one VLAN to another without a router,
however short the cable.

## Why bother

Three reasons, in the order they usually matter:

- **Broadcast containment.** Every broadcast reaches every port in the VLAN and
  no further. One noisy device stops being everybody's problem.
- **Separation.** The guest wifi and the finance PCs can share a switch and
  still not be able to reach each other.
- **Fewer switches.** One physical switch serves several logical networks.

## Access ports

An **access port** carries exactly one VLAN and the device plugged into it has
no idea the VLAN exists — frames arrive untagged, as ordinary Ethernet.

```
vlan 10
 name STAFF
vlan 20
 name GUEST
!
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
```

`switchport mode access` is worth typing even though a port usually defaults to
access: it stops the port ever negotiating itself into a trunk, which is both a
security problem and a source of very confusing outages.

## VLAN 1 is not special, except that it is

Every port starts in VLAN 1. That means a port you forget to configure is not
"off" — it is in VLAN 1 with every other port you forgot, which is its own
quiet broadcast domain. Leaving management traffic in VLAN 1 is discouraged for
exactly this reason: it is the VLAN everything lands in by accident.

## Checking

```
SW1# show vlan brief
VLAN  Name                  Status    Ports
1     default               active    FastEthernet0/4
10    STAFF                 active    FastEthernet0/1, FastEthernet0/3
20    GUEST                 active    FastEthernet0/2
```

A port in the wrong row is the whole bug, and it is visible at a glance.

## Your turn

The `switched` topology has four PCs on one switch, all in 10.0.0.0/24 and all
currently able to reach each other.

In `sw1.ios`, create VLAN 10 and VLAN 20 and place the ports:

| Port | PC | VLAN |
|---|---|---|
| FastEthernet0/1 | PC1 | 10 |
| FastEthernet0/2 | PC2 | 20 |
| FastEthernet0/3 | PC3 | 10 |
| FastEthernet0/4 | PC4 | 20 |

Afterwards PC1 must still reach PC3, and must **not** reach PC2 — even though
nothing about their IP addresses changed.
