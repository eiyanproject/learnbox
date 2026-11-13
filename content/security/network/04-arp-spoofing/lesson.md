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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **local network** (LAN) | the machines connected to the same switch or Wi-Fi |
| **MAC address** | the hardware address of a network card, such as `aa:bb:cc:dd:ee:ff`; used inside a local network |
| **IP address** | the logical address used to route packets between networks |
| **ARP** (Address Resolution Protocol) | how a machine finds the MAC address for an IP address on its local network |
| **ARP request** | a broadcast: "who has 192.168.0.1?" |
| **ARP reply** | "192.168.0.1 is at aa:aa:aa:aa:aa:aa" |
| **ARP cache** (ARP table, neighbour table) | the IP-to-MAC answers a machine has remembered |
| **broadcast** | a message sent to every machine on the local network |
| **unsolicited reply** (gratuitous ARP) | an ARP reply nobody asked for; most machines accept it anyway |
| **gateway** (default router) | the machine that connects the local network to the internet |
| **ARP spoofing** (ARP poisoning) | sending false ARP replies so that traffic for one IP goes to the attacker's MAC |
| **man in the middle** | an attacker who relays traffic between two parties while reading or changing it |
| **most recent wins** | a later reply overwrites an earlier one for the same IP |
| **conflict** | one IP claimed by two or more MAC addresses |
| **failover** | a backup machine taking over an address when the main one fails; a legitimate cause of conflicts |
| **DHCP** | the service that hands out IP addresses on a network |
| **allow-list** | known, legitimate exceptions that should not raise an alert |
| **dynamic ARP inspection** | a switch feature that drops ARP replies that do not match known leases |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `ip neigh` | shows your machine's ARP cache: IP, interface, MAC (`lladdr`) and state |
| `python arp.py` | runs your program: checks a short list of ARP packets for spoofing |

### Python names

| Name | What it does |
|---|---|
| `(ip, mac)` | one ARP packet: a claim that this IP is at this MAC |
| `table[ip] = mac` | stores or overwrites the MAC for that IP |
| `macs_by_ip.setdefault(ip, set()).add(mac)` | collects every distinct MAC seen for each IP |
| `len(macs) > 1` | more than one MAC for the same IP |
| `any(... for ip, mac in packets)` | `True` if at least one packet passes the test |

---

Inside a **local network**, machines deliver packets to each other by **MAC
address**, the hardware address of the network card, not by IP address. So
before sending anything, a machine has to find out which MAC belongs to the IP
it wants. **ARP** does that.

## How ARP works

1. Your machine wants to send to `192.168.0.1`. It **broadcasts** an ARP
   request to every machine on the network: "who has 192.168.0.1?"
2. The owner replies: "192.168.0.1 is at `aa:aa:aa:aa:aa:aa`".
3. Your machine stores the answer in its **ARP cache** and uses it for the
   next few minutes.

You can see your own cache with `ip neigh` (MAC addresses hidden here):

```text
192.168.0.14 dev wlp0s20f3 lladdr xx:xx:xx:xx:xx:xx REACHABLE
192.168.0.9 dev wlp0s20f3 lladdr xx:xx:xx:xx:xx:xx STALE
```

The catch: **ARP has no authentication at all**. Any machine can answer for
any IP. Most machines even accept replies nobody asked for, and they believe
the **most recent** one.

## The abuse

An attacker on the same network sends **unsolicited** ARP replies saying
"the **gateway's** IP is at my MAC". The gateway is the machine that connects
the network to the internet, so every other machine updates its cache and
starts sending all its internet traffic to the attacker.

The attacker passes the traffic on to the real gateway, so nothing looks
broken, while reading or changing it on the way. This is **ARP spoofing**,
and it turns anyone on a shared network (an office, a café's Wi-Fi) into a
potential **man in the middle**.

This is also why the certificates of Crypto lesson 6 matter: even on a
network where ARP has been spoofed, TLS stops the middle from reading or
changing the content, because the attacker cannot present a trusted
certificate for the real site.

## Spotting it

You detect ARP spoofing by watching ARP traffic for things that should not
happen:

- **One IP, two MACs.** Two machines are claiming the same address: the
  attacker is fighting the real owner.
- **The gateway's IP suddenly at a new MAC.** The classic takeover, and the
  most valuable target, because it captures everyone's outside traffic.

Both are rare in normal operation, so either is a strong signal, but not
proof. A **failover** pair sharing an address, a replaced network card, or a
**DHCP** lease moving from one machine to another can produce the same
pattern legitimately. That is why real monitors keep an **allow-list** of
known cases and alert on the rest. Managed switches can also prevent it with
**dynamic ARP inspection**, which drops replies that do not match the
addresses the network handed out.

This lesson stays on the defender's side: you build the detection, not the
attack.

## Your turn

In `arp.py` (each packet is `(ip, mac)`):

- `build_table(packets)`: the IP-to-MAC cache that results, with the most
  recent packet winning for each IP.
- `detect_conflict(packets)`: the set of IPs claimed by more than one MAC.
- `detect_gateway_takeover(packets, gateway_ip, real_mac)`: `True` if any
  packet claims the gateway's IP with a different MAC.

Run it:

```text
conflicts: {'192.168.0.1'}
takeover? True
```

## Check yourself

1. What does ARP do?
   *Finds the MAC address that belongs to an IP on the local network.*
2. Why is ARP easy to abuse?
   *It has no authentication, and machines believe the most recent reply.*
3. Why is the gateway the usual target?
   *All traffic to the internet goes through it.*
4. Name a legitimate reason for one IP to appear with two MACs.
   *Failover, a replaced network card, or a DHCP lease moving.*
5. The network is spoofed, but you visit an HTTPS site. Can the attacker read
   the page?
   *No: TLS encrypts it, and they cannot fake a trusted certificate.*
