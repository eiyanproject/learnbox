---
title: "Round 1: The dead link"
summary: Two routers, two LANs, and a ping that goes nowhere. Find the faults.
order: 1
files: [r1.ios, r2.ios]
run: python lab.py
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 150
---

Someone configured this network in a hurry and went home. PC1 cannot reach
PC2, and you have twelve minutes.

## The network

```text
PC1 ---- g0/0 [R1] g0/1 ==== g0/1 [R2] g0/0 ---- PC2
```

| Device | Interface | Address |
|---|---|---|
| PC1 | | 192.168.1.10/24, gateway 192.168.1.1 |
| R1 | g0/0 | 192.168.1.1/24 |
| R1 | g0/1 | 10.0.0.1/30 |
| R2 | g0/1 | 10.0.0.2/30 |
| R2 | g0/0 | 192.168.3.1/24 |
| PC2 | | 192.168.3.10/24, gateway 192.168.3.1 |

## The task

`r1.ios` and `r2.ios` hold the configuration as it was left. It has **four
faults** between the two files. Fix them so that the table above is what is
configured and PC1 and PC2 can ping each other in both directions.

The PCs are fine; do not look there. `python lab.py` runs the pings and says
where each one dies.
