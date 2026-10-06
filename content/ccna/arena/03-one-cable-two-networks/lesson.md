---
title: "Round 3: One cable, two networks"
summary: Two VLANs, one switch and a router on a single cable. The inter-VLAN routing is broken in four places.
order: 3
files: [sw1.ios, r1.ios]
run: python lab.py
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 700
---

Accounts and the warehouse sit on one switch in separate VLANs, and the only
way between them is the router hanging off a single cable. Since the weekend
nothing crosses it.

## The network

```text
PC1 -- Fa0/1 [SW1] Gi0/1 ======= Gi0/0 [R1]
PC2 -- Fa0/2
```

| VLAN | Subnet | Host | Gateway on R1 |
|---|---|---|---|
| 10 | 10.0.10.0/24 | PC1, 10.0.10.11 | Gi0/0.10, 10.0.10.1 |
| 20 | 10.0.20.0/24 | PC2, 10.0.20.11 | Gi0/0.20, 10.0.20.1 |

## The task

`sw1.ios` and `r1.ios` hold the configuration as it was left. There are
**four faults** between the two files. Fix them so that:

- PC1's port is an access port in VLAN 10 and PC2's in VLAN 20
- the link to the router is a trunk
- the router's physical interface is up, and each subinterface tags the
  right VLAN and holds that VLAN's gateway address
- PC1 and PC2 can ping each other, through the router

The PCs are configured correctly. `python lab.py` runs the pings and says
where each one dies.
