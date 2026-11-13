---
title: Port scanning, from both sides
summary: Reading a scan's replies to find open ports, and spotting the scan itself in the traffic it leaves behind.
order: 3
files: [scan.py]
run: python scan.py
hints:
  - "`open_ports`: a port answered SYN+ACK is open; one that answered with RST is closed. Return the sorted list of open ports."
  - "Each response is `(port, flags)` where flags is a set like `{'SYN', 'ACK'}` or `{'RST'}`."
  - "`detect_scan`: count the distinct destination ports each source touched; a source that hit more than `threshold` of them is scanning."
  - "The two sides use the same packets: the scanner reads the replies, the defender watches one source spray many ports."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **port scan** | asking a machine which services it runs, by probing its ports and reading the answers |
| **probe** | one test packet; in a SYN scan, a bare SYN |
| **open port** | a service is listening: the port answers SYN with SYN+ACK |
| **closed port** | nothing is listening: the port answers with RST |
| **filtered port** | no answer at all, usually because a firewall drops the packet |
| **listening** | a program is waiting for connections on that port |
| **attack surface** | everything on a machine an attacker could reach: here, its open ports |
| **SYN scan** (half-open scan) | send SYN, read the answer, never finish the handshake |
| **nmap** | the standard port scanner |
| **authorised** | you own the machine, or have written permission to test it; scan nothing else |
| **detection** | spotting an attack from the traces it leaves |
| **signature** | a pattern that identifies a kind of activity |
| **fan-out** | one source touching many different ports or hosts |
| **threshold** | the number above which an alert is raised |
| **intrusion detection system** (IDS) | software that watches traffic or logs for signs of attack |
| **false positive** | an alert for something harmless |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `ss -tln` | lists the TCP ports (`-t`) your own machine is listening on (`-l`), as numbers (`-n`) |
| `nmap localhost` | scans the 1,000 most common ports on your own machine |
| `nmap -p 1-1024 host` | scans ports 1 to 1024 |
| `nmap -sS host` | a SYN scan (needs root) |
| `python scan.py` | runs your program: reads three replies and checks a list of probes |

### Python names

| Name | What it does |
|---|---|
| `(port, flags)` | one reply: a port number and the set of flags it answered with |
| `{"SYN", "ACK"} <= flags` | `True` when both flags are in the set (`<=` means "is a subset of") |
| `[port for port, flags in responses if ...]` | the ports whose reply passes the test |
| `sorted(found)` | the list in ascending order |
| `d.setdefault(src, set())` | the set stored for `src`, creating an empty one the first time |
| `.add(port)` | puts the port in the set (a repeat is ignored) |
| `{src for src, ports in d.items() if len(ports) > threshold}` | the sources with more than `threshold` distinct ports |
| `range(1, 30)` | the numbers 1 to 29 |

---

A **port scan** asks a machine which services it runs, by knocking on its
ports and watching how each one answers. It is the first step of most
attacks, and also routine defence: you scan your **own** systems to find what
you have exposed by accident. This lesson looks at both sides, from the
packets.

Only scan machines you own or have written permission to test. In this
lab, that means `localhost` and the data in the exercise.

## The scanner's view: reading the replies

The scanner sends a bare `SYN` to a port, the first step of the handshake
from Network lesson 1, and reads what comes back:

| Reply | The port is | Because |
|---|---|---|
| `SYN+ACK` | **open** | a program is listening and is willing to connect |
| `RST` | **closed** | nothing is listening there |
| nothing | **filtered** | usually a firewall silently dropping the packet |

The open ports are the machine's **attack surface**: every one is a program
that strangers can talk to. A SYN scan never sends the final ACK, so no
connection is ever completed.

**nmap** is the standard tool. You can see your own machine's side of it
without scanning anything: `ss -tln` lists the ports it is listening on.
Python can knock on one port with a full connection, too:
`socket.socket().connect_ex(("127.0.0.1", 22))` returns `0` when the port is
open, and an error number such as `111` ("connection refused", the RST) when
it is closed.

## The defender's view: spotting the scan

The same packets look very different from the other side. A normal client
talks to the one or two ports it actually needs: 443 for a website, 22 for
SSH. A scanner sends SYNs to dozens or thousands of **different** ports from
one address in a short time. Nothing legitimate does that.

That **fan-out** is the scan's **signature**. Counting the distinct
destination ports for each source address is enough to catch a basic scan:

```text
10.0.0.9   ports 1, 2, 3, ... 29     29 distinct ports   -> scanning
10.0.0.20  port 443, 443, 443        1 distinct port     -> normal
```

Real **intrusion detection systems** also look at timing and rate, so a
slow scan spread over hours is still caught, and they tune the **threshold**
so that busy but normal machines do not cause **false positives**. But the
shape is this one.

This is the first lesson where you build **detection** rather than an
attack, and that is most of what defensive security is: knowing the normal
shape of traffic well enough that the abnormal stands out.

## Your turn

In `scan.py`:

- `open_ports(responses)`: from a list of `(port, flags_set)` replies, the
  sorted list of ports that answered `SYN+ACK`.
- `detect_scan(attempts, threshold=10)`: from a list of `(src_ip, dst_port)`
  connection attempts, the set of source addresses that touched **more than**
  `threshold` distinct ports.

Run it:

```text
open: [22, 80]
scanners: {'10.0.0.9'}
```

## Check yourself

1. A port answers a SYN with RST. Is it open, closed or filtered?
   *Closed.*
2. What does no reply at all usually mean?
   *Filtered: a firewall is dropping the probe.*
3. Why scan your own machines?
   *To find services you exposed by accident.*
4. What makes a scan stand out in traffic?
   *One source touching many distinct ports.*
5. A source sends 500 connections, all to port 443. Is it scanning?
   *Not by this test: it touched one distinct port.*
