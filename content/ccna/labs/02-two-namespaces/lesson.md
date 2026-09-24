---
title: "Lab: two hosts, one cable"
summary: Moving one end of a veth into a second namespace, which is how every container on your machine gets networking.
order: 2
files: [lab.sh]
run: python run.py
hints:
  - "Start a second namespace and keep it alive: `unshare -n sleep 60 &` then `peer=$!`. The namespace exists as long as that process does."
  - "`ip link set veth1 netns $peer` moves one end into the other namespace, addressed by the pid of a process living in it."
  - "Once moved, veth1 is gone from your namespace. Configure it with `nsenter -t $peer -n ip addr add 10.1.1.2/24 dev veth1`."
  - "Do not forget `nsenter -t $peer -n ip link set veth1 up` - the far end needs bringing up too, and it is easy to bring up only the end you can still see."
---

One namespace with two interfaces is useful for learning the commands. Two
namespaces joined by a cable is a network.

This is also, almost exactly, how container networking works. A container is a
set of namespaces; its "eth0" is one end of a veth pair whose other end lives
on the host, usually attached to a bridge. Once you have built it by hand, the
docker networking documentation stops being mysterious.

## Keeping a namespace alive

A namespace exists while something is in it. The idiom is to park a sleeping
process there and use its pid as the handle:

```bash
unshare -n sleep 60 >/dev/null 2>&1 &
peer=$!
```

The redirection matters more than it looks: a background process inherits your
standard output, and anything reading that output waits for *every* holder of
it to finish. Without the redirect, a tool collecting your script's output sits
there until the sleep expires.

`$!` is the pid of the last background job. That process is now the only
inhabitant of a brand new network namespace, and `$peer` is how everything else
refers to it.

## Moving an interface

```bash
ip link set veth1 netns $peer
```

The interface **leaves your namespace entirely**. `ip -br addr` will no longer
show it; it now belongs to the other side. This catches people out: the address
you carefully configured before moving it is discarded in the move, so
configure after, not before.

## Reaching in

```bash
nsenter -t $peer -n ip addr add 10.1.1.2/24 dev veth1
nsenter -t $peer -n ip link set veth1 up
```

`nsenter -t <pid> -n` runs one command inside that process's network namespace.
It is the manual version of what `ip netns exec` does for named namespaces —
which needs real root, so we use pids instead.

## What you have built

Two hosts on a point-to-point link, which is the `two-routers` /30 from the
static routing lesson, made real:

```
[ your namespace ]                 [ peer namespace ]
   veth0 10.1.1.1/24  <========>  veth1 10.1.1.2/24
```

A ping across it is genuine ICMP: ARP resolves, a request goes out one end and
comes back the other. If you get the mask wrong, or leave one end down, it
fails for the same reasons it would on real hardware.

## Your turn

In `lab.sh`:

- create the veth pair `veth0` / `veth1`
- start a second namespace and capture its pid in a variable called `peer`
- move `veth1` into it
- address `veth0` as 10.1.1.1/24 and `veth1` as 10.1.1.2/24, and bring both up

The test pings across and checks the far end really is in another namespace.
