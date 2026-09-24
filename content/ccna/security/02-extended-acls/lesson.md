---
title: Extended access lists
summary: Matching on destination and protocol as well as source, and why that changes where you put the list.
order: 2
files: [edge.ios]
run: python lab.py
hints:
  - "`ip access-list extended NAME` opens a named list; each rule is then `permit`/`deny` `<protocol>` `<source>` `<destination>`."
  - "`deny ip any host 8.8.8.8` blocks everyone from that one destination; `permit ip any any` after it lets everything else through."
  - "Order matters: put the deny first. A `permit ip any any` above it would match everything and the deny would never be reached."
  - "Apply it inbound on Gi0/0 with `ip access-group BLOCK_WEB in`."
---

A standard list can only ask who sent the packet. An extended list can ask
where it is going and what protocol it is, which is usually what you actually
want.

## The shape of a rule

```
ip access-list extended BLOCK_WEB
 deny ip any host 8.8.8.8
 permit ip any any
```

Each rule is `action protocol source destination`. Numbered extended lists
(100-199) work the same way:

```
access-list 100 deny ip any host 8.8.8.8
```

Named lists are better: the name says what the list is for, and you can edit
individual lines rather than deleting and retyping the whole thing.

## Address shorthand

| Written | Means |
|---|---|
| `any` | 0.0.0.0 255.255.255.255 — everything |
| `host 8.8.8.8` | that single address |
| `192.168.10.0 0.0.0.255` | that /24 |

`host X` and `X 0.0.0.0` are the same thing. `any` and `0.0.0.0 255.255.255.255`
are the same thing. The exam uses all four spellings.

## Placement flips

Standard lists go near the destination, because matching only on source means
placing them near the source would block that source from reaching everything.

Extended lists go **near the source**. Since they can match the exact
destination, you can drop unwanted traffic at the first router it meets, rather
than carrying it across the network to discard it at the far end. Filter early,
because forwarding a packet you intend to drop is wasted work on every link in
between.

That pair — standard near the destination, extended near the source — is a
reliable exam question.

## Order, again

First match wins, and the implicit deny is still at the end. Two rules in the
wrong order is the most common way an extended list "does nothing":

```
permit ip any any        <- everything matches here
deny ip any host 8.8.8.8 <- unreachable
```

## Your turn

The `edge` topology, NAT already configured in the starter.

In `edge.ios`, add a named extended list called `BLOCK_WEB` that stops **any**
host from reaching 8.8.8.8, while leaving everything else permitted, and apply
it inbound on Gi0/0.
