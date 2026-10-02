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

A **port scan** asks a host which services it is running by knocking on ports
and watching how they answer. It is the first move of most attacks and a routine
part of defending your own systems - you scan yourself to find what you have
accidentally exposed. Here is both sides of it, from the packets.

## Reading the replies (the scanner's view)

The scanner sends a bare `SYN` to a port and reads the reply:

- `SYN+ACK` - the port is **open**; a service is listening and completing the
  handshake.
- `RST` - the port is **closed**; nothing is listening.
- no reply at all - **filtered**, usually a firewall silently dropping it.

Collect the open ports and you have the host's attack surface. (`nmap` is the
standard tool, and in the terminal you can run it against `localhost` to see
exactly this.)

## Seeing the scan (the defender's view)

The same packets look very different from the other side. One source sending
`SYN`s to dozens of different ports in a short span is a pattern nothing
legitimate produces - a normal client talks to one or two ports it actually
wants. That fan-out is the **signature**, and counting distinct destination
ports per source is enough to catch a basic scan. Real intrusion-detection
systems add timing and rate, but the shape is this.

This is the first lesson where you build **detection** rather than an attack,
which is most of what defensive security actually is: knowing the normal shape
of traffic well enough that the abnormal stands out.

## Your turn

In `scan.py`:

- `open_ports(responses)` - from a list of `(port, flags_set)` replies, the
  sorted list of ports that answered `SYN+ACK`
- `detect_scan(attempts, threshold=10)` - from a list of `(src_ip, dst_port)`
  connection attempts, the set of source addresses that touched more than
  `threshold` distinct ports
