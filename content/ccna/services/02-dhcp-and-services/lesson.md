---
title: DHCP, NTP and logging
summary: "The services that make a network administrable: handing out addresses, agreeing on the time, and keeping a record."
order: 2
files: [r1.ios]
run: python lab.py
hints:
  - "`ip dhcp excluded-address 192.168.1.1 192.168.1.10` comes FIRST, before the pool. Exclude the addresses you configured by hand or DHCP will hand them out again."
  - "`ip dhcp pool LAN` then `network 192.168.1.0 255.255.255.0`, `default-router 192.168.1.1`, `dns-server 8.8.8.8`."
  - "A pool with no default-router leaves clients able to reach their own subnet and nothing else - they get an address and no way off the LAN."
  - "Interface addressing is the same as the first lesson: g0/0 is 192.168.1.1/24 and needs 'no shutdown'."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **DHCP** | hands out addresses to hosts automatically |
| **pool** | the range DHCP gives addresses from |
| **excluded address** | one DHCP must not hand out, such as the router's own |
| **duplicate address** | two hosts with one address: intermittent, horrible failures |
| **lease** | how long a host may keep its address, in days |
| **DNS server** | turns names into addresses |
| **DORA** | Discover, Offer, Request, Acknowledge: the DHCP exchange |
| **broadcast** | Discover and Request go to everyone on the subnet |
| **helper address** | forwards DHCP broadcasts to a server on another subnet |
| **NTP** | Network Time Protocol: keeps clocks in agreement |
| **syslog** | sends log messages to a central server |
| **severity** | 0 emergency to 7 debugging; 0 is the most severe |
| **`logging trap`** | the most verbose level sent: `informational` (6) sends 0 to 6 |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | applies your configuration to the lab topology and runs the pings |

### IOS commands

| Command | What it does |
|---|---|
| `ip dhcp excluded-address 192.168.1.1 192.168.1.10` | keeps a range out of the pool |
| `ip dhcp pool LAN` | creates a pool |
| `network 192.168.1.0 255.255.255.0` | its subnet |
| `default-router 192.168.1.1` | the gateway clients get |
| `dns-server 8.8.8.8` | the DNS server clients get |
| `lease 7` | a seven-day lease |
| `ip helper-address ADDRESS` | forwards DHCP to another subnet |
| `ntp server 216.239.35.0` | sets the time source |
| `logging host 192.168.1.50`, `logging trap informational` | syslog destination and level |

---

Three services appear on every exam and every real network, for the same
reason: without them a network works but cannot be run.

## DHCP

A router can hand out addresses for a subnet it is attached to:

```
ip dhcp excluded-address 192.168.1.1 192.168.1.10
!
ip dhcp pool LAN
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
 dns-server 8.8.8.8
 lease 7
```

**Exclude first.** The pool covers the whole subnet, including the router's own
address and any server you configured by hand. `ip dhcp excluded-address` is
what stops DHCP handing out an address something is already using — and the
symptom when you forget is an intermittent, and genuinely horrible, duplicate
address problem.

A pool needs `default-router` to be useful. Without it clients get an address
and can reach their own subnet only.

### DORA

The four-message exchange, worth memorising for the exam:

| | | |
|---|---|---|
| **D**iscover | client → broadcast | "is there a DHCP server?" |
| **O**ffer | server → client | "you can have this address" |
| **R**equest | client → broadcast | "I'll take it" |
| **A**cknowledge | server → client | "it's yours, here's the lease" |

Discover and Request are broadcasts, which is why a server on another subnet
needs `ip helper-address` on the router to forward them.

## NTP

```
ntp server 216.239.35.0
```

Clocks matter more than they look. Log entries from three devices are useless
if their timestamps disagree, certificates fail when the clock is wrong, and
some authentication protocols refuse to work at all.

## Syslog

```
logging host 192.168.1.50
logging trap informational
```

Severity runs 0 (emergency) to 7 (debugging), and `logging trap` sets how much
is sent. The number is a *maximum*: `informational` (6) sends levels 0 through
6 and drops debug.

Remember 0 is the most severe. It reads backwards from every other scale.

## Your turn

The `one-router` topology. In `r1.ios`:

- address GigabitEthernet0/0 as 192.168.1.1/24 and bring it up
- exclude 192.168.1.1 through 192.168.1.10
- create a pool called `LAN` for 192.168.1.0/24 with the router as the default
  gateway and 8.8.8.8 for DNS
