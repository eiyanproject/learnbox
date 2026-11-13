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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **fault** | a mistake in the configuration; there are four |
| **`/24`**, **`/30`** | prefix lengths: 256 addresses / 4 addresses (a point-to-point link) |
| **mask** | `255.255.255.0` for /24, `255.255.255.252` for /30 |
| **gateway** | the router address each PC sends other traffic to |
| **both directions** | a ping must get there and back; the return path needs routes too |
| **`g0/0`** | short for `GigabitEthernet0/0` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | runs the pings and says where each one dies |

### IOS commands

| Command | What it does |
|---|---|
| `interface`, `ip address`, `no shutdown` | the address commands from Fundamentals |
| `ip route NETWORK MASK NEXT-HOP` | a static route |
| `show ip interface brief`, `show ip route` | check interfaces and routes |

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
