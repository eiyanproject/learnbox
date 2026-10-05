---
title: "Round 2: Two floors"
summary: Two switches, two VLANs and one link between them. Half of it is wrong.
order: 2
files: [sw1.ios, sw2.ios]
run: python lab.py
challenge:
  minutes: 15
  xp: 200
  requires:
    xp: 500
---

Sales and Engineering each have people on both floors. Each team should see
its own people and nobody else, and right now nothing crosses the stairs.

## The network

```text
PC1 -- Fa0/1 [SW1] Fa0/2 -- PC2
               | Gi0/1
               | Gi0/1
PC3 -- Fa0/1 [SW2] Fa0/2 -- PC4
```

| VLAN | Team | Members |
|---|---|---|
| 10 | Sales | PC1, PC3 |
| 20 | Engineering | PC2, PC4 |

## The task

Finish `sw1.ios` and `sw2.ios`. SW1 was started and has mistakes in it; SW2
has barely been touched. When you are done:

- both VLANs exist on both switches
- each PC's port is an access port in its team's VLAN
- the link between the switches is a trunk at both ends, carrying VLANs 10
  and 20
- PC1 reaches PC3, PC2 reaches PC4, and Sales cannot reach Engineering

`python lab.py` runs the two pings that should work.
