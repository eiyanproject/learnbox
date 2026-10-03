---
title: ARP spoofing on the local network
summary: How a machine finds its neighbours, how that trust is abused to sit in the middle, and how to spot it happening.
order: 4
files: [arp.py]
run: python arp.py
hints:
  - "`build_table`: ARP caches take the most recent answer, so later packets overwrite earlier ones for the same IP."
  - "Each packet is `(ip, mac)` - a claim that this IP is at this MAC."
  - "`detect_conflict`: collect the distinct MACs seen for each IP; an IP claimed by more than one MAC is the sign of spoofing."
  - "`detect_gateway_takeover`: any packet claiming the gateway's IP with a MAC other than its real one is an attacker redirecting the network's traffic."
---

On a local network, machines find each other by **MAC address**, not IP. **ARP**
is the protocol that maps one to the other: "who has 192.168.0.1?" and the owner
replies "that's me, at this MAC." The catch is that ARP has no authentication
whatsoever - any machine can answer for any IP, and hosts believe the most
recent reply.

## The abuse

An attacker on the same network sends unsolicited ARP replies claiming the
**gateway's** IP is at the attacker's MAC. Every other machine updates its cache
and starts sending the attacker all traffic bound for the internet. The attacker
forwards it on - so nothing looks broken - while reading and modifying it in
transit. This is ARP spoofing, and it turns a shared local network into a
**man-in-the-middle** position. (It is also why the authentication from the PKI
lesson matters: even on a compromised network, TLS stops the middle from reading
the content.)

## Spotting it

You detect it by watching the ARP traffic for impossibilities:

- **one IP, two MACs** - two machines claiming the same address, the attacker
  fighting the real owner
- **the gateway's IP suddenly at a new MAC** - the classic takeover

Both are rare in normal operation, so either is a strong signal - but not proof.
A failover pair sharing an address, a replaced network card or a DHCP lease
moving between machines can produce the same pattern legitimately, which is why
real monitors keep an allow-list of known cases and alert on the rest. This stays
firmly on the defender's side: you are building the detection, not the attack.

## Your turn

In `arp.py` (each packet is `(ip, mac)`):

- `build_table(packets)` - the resulting IP-to-MAC cache, most-recent-wins
- `detect_conflict(packets)` - the set of IPs claimed by more than one MAC
- `detect_gateway_takeover(packets, gateway_ip, real_mac)` - `True` if any packet
  claims the gateway's IP with a different MAC
