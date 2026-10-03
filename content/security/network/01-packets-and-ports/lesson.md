---
title: Packets, ports and flags
summary: What a packet actually is in bytes - the addresses, the ports, and the TCP flags that reveal a handshake or a scan.
order: 1
files: [packet.py]
run: python packet.py
hints:
  - "IPv4 and TCP header fields are big-endian. `data[12:16]` of the IP header are the source address bytes; join them with dots."
  - "`parse_ipv4`: the low nibble of byte 0 is the header length in 32-bit words (so `* 4` for bytes); byte 9 is the protocol (6 = TCP); bytes 12-16 and 16-20 are the addresses."
  - "`tcp_flag_names`: the flags byte has FIN=1, SYN=2, RST=4, PSH=8, ACK=16, URG=32. Return the set of names whose bit is set."
  - "`is_syn_only`: exactly the SYN flag and nothing else - a bare connection attempt, and the probe a port scan sends."
---

Everything on a network is **packets**, and tools like Wireshark and `tcpdump`
are just readers for their bytes. Knowing the layout means you can read a
capture, craft a probe, or recognise an attack in traffic - so start with the
bytes themselves.

## The layers

A packet is headers wrapped around headers. Peeling from the outside: an
**Ethernet** frame carries an **IP** packet, which carries a **TCP** (or UDP)
segment, which carries your data. Each header is a fixed, documented layout.

**IPv4** (20 bytes, usually) carries the **addresses**: who sent it, who it is
for. The fields you reach for first:

- byte 0: the high nibble is the version (4 for IPv4); the low nibble is the
  header length in 32-bit words, so `5` means 20 bytes
- byte 9: protocol (6 = TCP, 17 = UDP, 1 = ICMP)
- bytes 12-15: source address; bytes 16-19: destination

**TCP** carries the **ports** - which service - and the flags that drive the
connection. Source and destination ports are the first two 16-bit fields, and
the flags are byte 13. A
port is how one machine runs many services at once: 80 is HTTP, 443 HTTPS, 22
SSH, 53 DNS.

Multi-byte fields are **big-endian** (network byte order), which `struct` reads
with the `!` prefix.

## Flags, and what they tell you

A single byte of TCP flags drives every connection, and reading it is how you
tell normal traffic from a probe:

| bit | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| flag | FIN | SYN | RST | PSH | ACK | URG |

The **three-way handshake** that opens every TCP connection is three flag
combinations: the client sends `SYN`, the server replies `SYN+ACK`, the client
answers `ACK`. A lone `SYN` to a port is a connection attempt - and a flood of
lone `SYN`s to many ports is a **port scan**, which is where the next lessons
go.

## Your turn

In `packet.py` (headers are `bytes`; addresses come back as dotted strings):

- `parse_ipv4(data)` - `{version, ihl, protocol, src, dst}`, with `ihl` as the
  header length in **bytes** (the field's value times 4)
- `parse_tcp(data)` - `{src_port, dst_port, flags}` where `flags` is a set of
  names
- `tcp_flag_names(flags_byte)` - the set of flag names set in the byte
- `is_syn_only(flags_byte)` - `True` for exactly SYN, the scan probe
