---
title: Standard access lists
summary: Permitting and denying by source address, the implicit deny that catches everyone, and where to apply the list.
order: 1
files: [edge.ios]
run: python lab.py
hints:
  - "Start from a working NAT config - the same one as the IP Services lesson - then add the filtering on top."
  - "`access-list 20 deny 192.168.10.12 0.0.0.0` blocks PC2. A wildcard of 0.0.0.0 means every bit must match, i.e. exactly that host; `host 192.168.10.12` is the readable equivalent."
  - "Follow it with `access-list 20 permit any` or the implicit deny at the end blocks PC1 as well."
  - "Apply it with `ip access-group 20 in` on Gi0/0 - inbound on the interface where the traffic arrives."
---

An access list is an ordered list of permit and deny rules. A packet is tested
against each in turn and the **first match wins**; nothing after it is
consulted.

## Standard lists match the source only

```
access-list 20 deny 192.168.10.12 0.0.0.0
access-list 20 permit any
```

Numbered 1-99 (and 1300-1999), a standard list can only ask *who sent this*.
It cannot ask where the packet is going, or what protocol it is. That
limitation drives where you put it.

## The implicit deny

Every access list ends with an invisible `deny any`. It is not shown in the
configuration and it is always there.

The consequence is the single most common ACL mistake: a list that permits one
thing blocks *everything else*, including traffic nobody intended to filter.
If you write

```
access-list 30 permit 192.168.10.11 0.0.0.0
```

you have not permitted one host, you have denied every other host on the
network. Which may be what you wanted — but it is worth knowing it is what you
said.

## Order matters

Rules are evaluated top to bottom, so a broad permit above a specific deny makes
the deny unreachable:

```
access-list 40 permit any               <- matches everything
access-list 40 deny 192.168.10.12 0.0.0.0   <- never reached
```

Specific rules first, general rules last. Always.

## Where to apply it

```
interface GigabitEthernet0/0
 ip access-group 20 in
```

`in` and `out` are from the **router's** point of view: `in` is traffic
arriving on that interface, `out` is traffic leaving it.

The traditional advice is to put a standard list **close to the destination**.
The reason is that it can only match the source, so placing it near the source
would block that source from reaching everything, not just the thing you meant
to protect.

## Your turn

The `edge` topology with NAT already working. In `edge.ios`, add an access list
numbered 20 that stops **PC2** (192.168.10.12) from reaching the internet while
leaving PC1 working, and apply it inbound on Gi0/0.

The NAT configuration is already in the starter file — add to it, do not
replace it.
