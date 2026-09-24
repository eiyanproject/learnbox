---
title: "Lab: a real interface"
summary: The same ideas as lesson one, in the kernel instead of a simulator - veth pairs, addresses, and why loopback starts down.
order: 1
files: [lab.sh]
run: python run.py
hints:
  - "`ip link add veth0 type veth peer name veth1` creates BOTH ends at once. A veth is always a pair - it is a virtual cable, and a cable has two ends."
  - "`ip addr add 10.1.1.1/24 dev veth0` uses prefix notation here, not a dotted mask. This is Linux, not IOS."
  - "Both ends need bringing up separately: `ip link set veth0 up` and `ip link set veth1 up`. Same idea as 'no shutdown', different words."
  - "Give veth0 10.1.1.1/24 and veth1 10.1.1.2/24 so the two ends are in the same subnet and can reach each other."
---

Everything so far has been a simulator. This runs on the actual Linux
networking stack: real interfaces, real ARP, real ICMP. If you get it wrong the
kernel tells you, not a model of one.

It is safe because it happens inside a **network namespace** — a private copy
of the entire networking stack, with its own interfaces and routing table. The
namespace is created by `unshare -Urn`, needs no privileges, and vanishes when
the process exits. Nothing you do here can affect the machine.

## veth pairs

A **veth** is a virtual cable. It always comes in pairs, because a cable with
one end is not a cable:

```bash
ip link add veth0 type veth peer name veth1
```

That one command creates two interfaces. Whatever goes in one end comes out the
other. It is the building block for everything that follows — connecting two
namespaces, attaching something to a bridge, or just having two interfaces to
experiment with.

## The vocabulary, side by side

| Cisco IOS | Linux |
|---|---|
| `show ip interface brief` | `ip -br addr` |
| `interface g0/0` + `ip address 10.1.1.1 255.255.255.0` | `ip addr add 10.1.1.1/24 dev veth0` |
| `no shutdown` | `ip link set veth0 up` |
| `shutdown` | `ip link set veth0 down` |
| `show ip route` | `ip route` |
| `ping 10.1.1.2` | `ping -c1 10.1.1.2` |

Two differences worth noticing. Linux takes a **prefix length**, never a dotted
mask. And an interface can hold several addresses at once — `ip addr add` is
genuinely additive, where the IOS command replaces.

## Loopback starts down

A fresh namespace has one interface, `lo`, and it is **down**. This surprises
everyone once: `ping 127.0.0.1` fails inside a new namespace until you run
`ip link set lo up`. Plenty of software assumes loopback works and fails in
confusing ways when it does not.

The lab harness brings `lo` up for you before your script runs, so you can
concentrate on the rest — but it is worth knowing it was not up to begin with.

## Your turn

In `lab.sh`, using `ip` commands:

- create a veth pair called `veth0` and `veth1`
- give `veth0` the address 10.1.1.1/24 and `veth1` 10.1.1.2/24
- bring both ends up

Run `python run.py` to build it and see whether the two ends can ping each
other. To poke at it by hand, get your own namespace with:

```bash
unshare -Urn bash
```
