---
title: "Lab: a bridge is a switch"
summary: Building a three-port switch out of a Linux bridge, and watching one broadcast domain behave exactly like the simulator said it would.
order: 3
files: [lab.sh]
run: python run.py
hints:
  - "`ip link add br0 type bridge` creates the switch; `ip link set br0 up` brings it up. A bridge that is down forwards nothing."
  - "Each host needs its own veth pair: one end goes into the bridge, the other keeps the address. Name them predictably, e.g. `h1`/`h1br`."
  - "`ip link set h1br master br0` is the equivalent of plugging a cable into a switch port. Both the port and the host end need `up`."
  - "Give the bridge side NO address - a switch port has no IP. Put 10.0.0.1/24, .2 and .3 on h1, h2, h3 and let the bridge switch between them."
---

A Linux bridge is a switch. Not "like" a switch — it learns MAC addresses,
floods what it does not know, and forwards within one broadcast domain, which
is the definition.

Building one makes the VLAN lessons concrete: everything attached to one bridge
is one broadcast domain, exactly as everything in one VLAN was.

## The pieces

```bash
ip link add br0 type bridge
ip link set br0 up
```

Then for each host, a veth pair with one end in the bridge:

```bash
ip link add h1 type veth peer name h1br
ip link set h1br master br0      # plug this end into the switch
ip link set h1br up              # the switch port
ip addr add 10.0.0.1/24 dev h1   # the host end keeps the address
ip link set h1 up
```

`master br0` is the cable going into the switch port. The bridge side gets **no
address** — a switch port does not have one, and giving it one is a
misunderstanding worth avoiding early. The address belongs to the host.

## What you can see

```bash
bridge link          # which ports belong to the bridge
bridge fdb show      # the MAC address table it has learned
ip -br addr          # everything at once
```

`bridge fdb show` is the real version of `show mac address-table`. Ping between
two hosts and watch entries appear: the bridge learned where each MAC lives
from the frames it saw, which is exactly the learning behaviour a switch has.

## The thing worth noticing

Three hosts on one bridge can all reach each other, and **none of them has a
route to the others** — `ip route` shows only the connected subnet. No routing
is involved at all. They are in one broadcast domain, so ARP finds the
destination directly and the bridge delivers the frame.

That is the entire difference between layer 2 and layer 3 in one observation.
The moment you put a host in a different subnet, it stops working, and you need
a router.

## Your turn

In `lab.sh`, build a three-port switch:

- a bridge `br0`, up
- three veth pairs: `h1`/`h1br`, `h2`/`h2br`, `h3`/`h3br`
- each `*br` end attached to `br0` with `master br0`, and up
- addresses 10.0.0.1/24, 10.0.0.2/24 and 10.0.0.3/24 on `h1`, `h2` and `h3`,
  all up

All three must be able to reach each other.
