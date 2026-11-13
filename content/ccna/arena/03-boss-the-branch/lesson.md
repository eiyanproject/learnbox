---
title: "Boss: The branch office"
summary: Three unconfigured routers between a PC and a server. Address them, route them, and lock the server down.
order: 4
files: [r1.ios, r2.ios, r3.ios]
run: python lab.py
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 900
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **default route** | `0.0.0.0 0.0.0.0`: where traffic goes when nothing more specific matches |
| **static route** | a route you type in yourself |
| **LAN** | the local network behind a router |
| **standard access list** | an ACL matching only the source address |
| **outbound** | applied to traffic leaving an interface |
| **implicit deny** | every ACL ends by denying whatever it did not permit |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | runs the PC-to-server pings |

### IOS commands

| Command | What it does |
|---|---|
| `interface`, `ip address`, `no shutdown` | addresses |
| `ip route 0.0.0.0 0.0.0.0 NEXT-HOP` | a default route |
| `ip route NETWORK MASK NEXT-HOP` | a route to one LAN |
| `access-list 10 permit NETWORK WILDCARD` | a standard ACL entry |
| `ip access-group 10 out` | applies it outbound on an interface |

---

Three routers came out of their boxes this morning. By the time the clock
runs out the branch PC must reach the server, and nothing else may.

## The network

```text
PC1 --- g0/0 [R1] g0/1 === g0/1 [R2] g0/2 === g0/2 [R3] g0/0 --- SRV
```

| Device | Interface | Address |
|---|---|---|
| PC1 | | 172.16.1.10/24, gateway 172.16.1.1 |
| R1 | g0/0 | 172.16.1.1/24 |
| R1 | g0/1 | 10.1.12.1/30 |
| R2 | g0/1 | 10.1.12.2/30 |
| R2 | g0/2 | 10.1.23.1/30 |
| R3 | g0/2 | 10.1.23.2/30 |
| R3 | g0/0 | 172.16.9.1/24 |
| SRV | | 172.16.9.10/24, gateway 172.16.9.1 |

## The task

Write all three configurations from nothing.

1. **Addresses.** Every interface in the table, with the right mask, brought
   up.
2. **Routing, with static routes.** R1 and R3 are at the ends of the chain:
   give each of them a single default route towards R2 and nothing else. R2
   sits in the middle and needs one route to each LAN.
3. **Protect the server.** On R3, write standard access list `10` so that
   only the branch LAN, 172.16.1.0/24, may reach the server's subnet, and
   apply it **outbound** on g0/0. A ping from R2 itself must be stopped by
   it; a ping from PC1 must get through.

PC1 and SRV must be able to ping each other in both directions, by way of
all three routers. `python lab.py` runs those pings.
