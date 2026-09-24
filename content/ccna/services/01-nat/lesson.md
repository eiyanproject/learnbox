---
title: NAT and the address you actually leave with
summary: Why a private address cannot cross the internet, and how one public address serves a whole office.
order: 1
files: [edge.ios]
run: python lab.py
hints:
  - "Mark the boundary first: `ip nat inside` on Gi0/0 (the LAN side) and `ip nat outside` on Gi0/1 (towards the ISP). NAT does nothing until it knows which side is which."
  - "EDGE needs a default route out: `ip route 0.0.0.0 0.0.0.0 203.0.113.1`."
  - "An access list selects who gets translated: `access-list 1 permit 192.168.10.0 0.0.0.255`."
  - "Then `ip nat inside source list 1 interface GigabitEthernet0/1 overload` - 'overload' is the word that makes it PAT, sharing one address across many hosts by port number."
---

192.168.10.11 is not an address anyone on the internet can reply to. RFC 1918
set aside three ranges for private use — 10.0.0.0/8, 172.16.0.0/12,
192.168.0.0/16 — and every router on the public internet drops them.

So a packet from the office has to leave wearing a different address. That
rewriting is NAT.

## The boundary

NAT has no idea which of your interfaces faces the world unless you tell it:

```
interface GigabitEthernet0/0
 ip nat inside
!
interface GigabitEthernet0/1
 ip nat outside
```

Getting these backwards, or leaving one off, is the most common reason a
perfectly correct NAT statement does nothing at all.

## Two ways to translate

**Static NAT** maps one private address to one public address, permanently:

```
ip nat inside source static 192.168.10.11 203.0.113.10
```

Use it for something that must be reachable *from* outside, like a web server.

**PAT** (NAT overload) shares one public address across every host, keeping
them apart by source port:

```
access-list 1 permit 192.168.10.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Read it as: *hosts matching list 1, leaving via Gi0/1, share its address*. The
word `overload` is what makes it many-to-one. Without it you have dynamic NAT
from a pool, and you run out of addresses when the pool does.

This is what almost every home and office connection does, and why thousands
of devices can share a single public address.

## The vocabulary the exam uses

| Term | Means |
|---|---|
| Inside local | the private address, as the host knows itself |
| Inside global | what that host looks like from outside |
| Outside global | the real address of the far server |
| Outside local | how the far server appears to the inside |

"Inside/outside" is whose address it is; "local/global" is which side you are
looking from.

## Why the ping fails without it

Leave NAT off and the echo request still reaches the server: the ISP forwards
towards 8.8.8.8 happily. It is the **reply** that dies, because the ISP has no
route back to 192.168.10.11 and would not use one if it did. Half the path
works, which is exactly the failure this simulator reports.

## Your turn

The `edge` topology: two PCs behind EDGE, an ISP router, and a server at
8.8.8.8. ISP is already configured.

In `edge.ios`:

| Interface | Address | Role |
|---|---|---|
| GigabitEthernet0/0 | 192.168.10.1/24 | inside |
| GigabitEthernet0/1 | 203.0.113.2/30 | outside |

Add a default route towards 203.0.113.1, and PAT so both PCs can reach the
server.
