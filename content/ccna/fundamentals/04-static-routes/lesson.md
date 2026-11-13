---
title: Static routes, and the return path
summary: Telling a router about a subnet it is not attached to - and why configuring only one end leaves the ping failing.
order: 4
files: [r1.ios, r2.ios]
run: python lab.py
hints:
  - "Three interfaces to address: R1 g0/0 (192.168.1.1/24), the link R1 g0/1 (10.0.0.1) to R2 g0/1 (10.0.0.2) as a /30 with mask 255.255.255.252, and R2 g0/0 (192.168.3.1/24). All with `no shutdown`."
  - "The syntax is `ip route <network> <mask> <next-hop>`: on R1, `ip route 192.168.3.0 255.255.255.0 10.0.0.2`."
  - "The next hop must be an address R1 can already reach directly - the far end of the link, not a router two hops away."
  - "Now do it in reverse. R2 needs `ip route 192.168.1.0 255.255.255.0 10.0.0.1`, or the echo request arrives and the reply has nowhere to go."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **static route** | a route you type in: network, mask, next hop |
| **next hop** | the neighbour to send to; must be reachable through a connected interface |
| **`S`** | marks a static route in `show ip route` |
| **`[1/0]`** | administrative distance / metric |
| **administrative distance** | how trusted a route source is; static is 1 |
| **/30 link** | four addresses, two usable: the usual link between routers |
| **echo request** / **echo reply** | the two halves of a ping, travelling opposite ways |
| **return path** | the route home; every route needs a matching one |
| **traceroute** | shows each hop a packet takes |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | applies your configuration to the lab topology and runs the pings |

### IOS commands

| Command | What it does |
|---|---|
| `ip route 192.168.3.0 255.255.255.0 10.0.0.2` | to reach 192.168.3.0/24, send to 10.0.0.2 |
| `show ip route` | the routing table |
| `traceroute ADDRESS` | lists the hops |

---

A router knows the subnets it is attached to. Everything else has to be
learned — by a routing protocol, or by you.

## The command

```
ip route 192.168.3.0 255.255.255.0 10.0.0.2
          |            |             |
          network      mask          next hop
```

Read it as a sentence: *to reach 192.168.3.0/24, send it to 10.0.0.2*. The next
hop must be an address the router can already reach through a connected
interface. Pointing at a router two hops away does not work, because the
router has no way to deliver the frame.

In `show ip route` your static routes appear as `S`:

```
C        10.0.0.0/30 is directly connected, GigabitEthernet0/1
C        192.168.1.0/24 is directly connected, GigabitEthernet0/0
S        192.168.3.0/24 [1/0] via 10.0.0.2
```

The `[1/0]` is administrative distance and metric. A static route's distance
of 1 beats almost everything, which is why a static route pointing somewhere
wrong is so effective at breaking a network.

## The /30 between routers

The link between two routers needs only two usable addresses, so it is
traditionally a /30 — mask 255.255.255.252, four addresses, two usable. A /24
would work and waste 252 addresses, and the exam expects you to know why you
would not.

## The half that people forget

Here is the failure that shows up in every lab and on every exam:

> I added the route on R1 and the ping still fails.

Of course it does. The echo **request** now finds its way to PC2. The echo
**reply** is a separate packet, travelling the other way, and R2 has never
heard of 192.168.1.0/24. It drops it.

Routing is not a property of a path; it is a decision each router makes,
independently, for each packet, in one direction. Every route you add needs a
matching route home. This simulator checks the return path for exactly this
reason — a one-way path is reported as unreachable, as it would be on real kit.

When something half-works, ask *which direction is broken* before anything
else. `traceroute` from both ends localises it in seconds.

## Your turn

The topology is `two-routers`:

```
PC1 --- R1 =========== R2 --- PC2
     .1  g0/1     g0/1  .1
192.168.1.0/24  10.0.0.0/30  192.168.3.0/24
```

| Device | Interface | Address | Mask |
|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |
| R1 | GigabitEthernet0/1 | 10.0.0.1 | 255.255.255.252 |
| R2 | GigabitEthernet0/1 | 10.0.0.2 | 255.255.255.252 |
| R2 | GigabitEthernet0/0 | 192.168.3.1 | 255.255.255.0 |

Configure both routers in `r1.ios` and `r2.ios`, add the static route each one
needs, and get PC1 and PC2 talking **both ways**.
