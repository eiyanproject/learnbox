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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **packet** | one unit of data sent over a network: headers followed by a payload |
| **header** | the fixed-layout bytes at the front that say where the packet goes and how to handle it |
| **payload** | the data the packet carries after its headers |
| **layer** | one header wrapped inside another: Ethernet, then IP, then TCP or UDP, then data |
| **Ethernet frame** | the outermost layer on a local network, with MAC addresses |
| **IP** (Internet Protocol) | the layer with the **IP addresses**: who sent the packet and who it is for |
| **IPv4** | the version with four-number addresses such as `192.168.1.5` |
| **dotted address** | an IPv4 address written as four bytes in decimal, separated by dots |
| **TCP** | the reliable, connection-based layer above IP, with ports and flags |
| **UDP** | a simpler layer with ports but no connections (DNS uses it) |
| **ICMP** | messages about the network itself, such as `ping` |
| **protocol number** | byte 9 of the IPv4 header: 6 TCP, 17 UDP, 1 ICMP |
| **port** | a number from 0 to 65535 that picks one service on a machine: 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS |
| **nibble** | half a byte: four bits, one hex digit |
| **IHL** (internet header length) | the low nibble of byte 0: the IPv4 header length in 4-byte words, so `5` is 20 bytes |
| **big-endian** (network byte order) | multi-byte numbers stored most significant byte first |
| **flag** | one bit of the TCP flags byte that marks the packet's purpose |
| **SYN** | "let us start a connection" |
| **ACK** | "I received your data" |
| **FIN** | "I have finished sending" |
| **RST** | "reset: no such connection, or go away" |
| **PSH**, **URG** | "deliver this now"; "urgent data" (rare) |
| **three-way handshake** | how every TCP connection opens: SYN, SYN+ACK, ACK |
| **port scan** | probing many ports to see which answer; lone SYNs to many ports are its signature |
| **probe** | one packet sent to test something |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `tcpdump -nn -i any` | shows packets as they pass, without turning addresses or ports into names |
| `tcpdump -X` | also shows each packet's bytes in hex and ASCII |
| `python packet.py` | runs your program: names the flags of a SYN+ACK and tests a bare SYN |

### Python names

| Name | What it does |
|---|---|
| `bytes.fromhex("4500...")` | bytes made from hex digits |
| `data[0] >> 4` | the high nibble of the first byte |
| `data[0] & 0x0F` | the low nibble |
| `data[12:16]` | bytes 12, 13, 14 and 15 |
| `".".join(str(b) for b in ...)` | the bytes written as decimal numbers with dots between |
| `int.from_bytes(data[0:2], "big")` | two bytes read as one big-endian number |
| `struct.unpack("!H", ...)` | another way to do it: `!` is network byte order, `H` a 2-byte number |
| `flags_byte & bit` | non-zero when that flag's bit is set |
| `{name for bit, name in FLAGS if ...}` | a set built from the names that pass the test |
| `FLAGS` | given to you: the list of `(bit value, name)` pairs |
| `sorted(s)` | a set's items as a sorted list, so they print in a fixed order |

---

Everything on a network travels as **packets**, and tools like Wireshark and
`tcpdump` are readers for their bytes. If you know the layout, you can read a
capture, build a test packet, or recognise an attack in traffic. So start with
the bytes themselves.

## Layers

A packet is headers wrapped in headers, like envelopes inside envelopes. From
the outside in:

```text
[ Ethernet | IP | TCP | data ]
```

- **Ethernet** gets the packet across the local network (Network lesson 4).
- **IP** gets it across the internet: it carries the **addresses**.
- **TCP** (or UDP) gets it to the right program on that machine: it carries
  the **ports**.
- Then the **payload**, the actual data, such as an HTTP request.

Each header has a fixed, documented layout. This lesson reads the IP and TCP
headers.

## The IPv4 header

An IPv4 header is usually 20 bytes. The fields you look at first:

| Byte(s) | Field | Notes |
|---|---|---|
| 0, high nibble | version | 4 for IPv4 |
| 0, low nibble | header length (IHL) | in 4-byte words, so `5` means 20 bytes |
| 9 | protocol | 6 TCP, 17 UDP, 1 ICMP |
| 12 to 15 | source address | who sent it |
| 16 to 19 | destination address | who it is for |

A **nibble** is half a byte, one hex digit. In the byte `0x45`, the high
nibble is `4` (the version) and the low nibble is `5` (the length).

```pycon
>>> from packet import parse_ipv4
>>> ip = bytes.fromhex("450000280001000040060000c0a80105c0a80101")
>>> parse_ipv4(ip)
{'version': 4, 'ihl': 20, 'protocol': 6, 'src': '192.168.1.5', 'dst': '192.168.1.1'}
```

Byte 12 onwards is `c0 a8 01 05`, which is 192, 168, 1, 5: the source
address, written **dotted**.

## The TCP header

TCP carries the **ports**. A port is how one machine runs many services at
once: the same address can answer SSH on 22, DNS on 53, HTTP on 80 and HTTPS
on 443.

| Byte(s) | Field |
|---|---|
| 0 to 1 | source port |
| 2 to 3 | destination port |
| 13 | the flags |

Numbers longer than one byte are **big-endian** (also called network byte
order): the most significant byte comes first. `int.from_bytes(b, "big")`
reads them, and so does `struct` with a `!` at the start of its format.

```pycon
>>> from packet import parse_tcp
>>> tcp = bytes.fromhex("d431001600000000000000005002040000000000")
>>> p = parse_tcp(tcp)
>>> p["src_port"], p["dst_port"], sorted(p["flags"])
(54321, 22, ['SYN'])
```

`d4 31` is 54321 and `00 16` is 22: some program is trying to connect to SSH.

## Flags, and what they tell you

Byte 13 holds the **flags**, one bit each:

| Bit value | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| Flag | FIN | SYN | RST | PSH | ACK | URG |

A byte can have several bits set: `0x12` is 16 + 2, so ACK and SYN.

```pycon
>>> from packet import tcp_flag_names
>>> sorted(tcp_flag_names(0x12))
['ACK', 'SYN']
>>> sorted(tcp_flag_names(0x18))     # 16 + 8: data being delivered
['ACK', 'PSH']
```

Every TCP connection opens with the **three-way handshake**:

```text
client ──SYN──────> server     "let us connect"
client <──SYN+ACK── server     "agreed"
client ──ACK──────> server     "connected"
```

A closed port answers a SYN with RST. So a lone SYN to a port is one
connection attempt, and a burst of lone SYNs to many ports from one address is
a **port scan**: someone mapping which services a machine runs. That is where
the next lessons go.

## Your turn

In `packet.py` (headers are `bytes`; addresses come back as dotted strings):

- `parse_ipv4(data)`: a dict `{version, ihl, protocol, src, dst}`, with `ihl`
  as the header length in **bytes** (the field's value times 4).
- `parse_tcp(data)`: a dict `{src_port, dst_port, flags}`, where `flags` is
  a set of names.
- `tcp_flag_names(flags_byte)`: the set of names of the flags set in the
  byte.
- `is_syn_only(flags_byte)`: `True` for exactly SYN and nothing else, the
  scan probe.

## Check yourself

1. Which header carries the addresses, and which the ports?
   *IP carries the addresses; TCP or UDP carries the ports.*
2. Byte 0 of an IPv4 header is `0x45`. What does it say?
   *Version 4, header length 5 words: 20 bytes.*
3. What is the flags byte `0x11`?
   *16 + 1: ACK and FIN.*
4. What are the three packets of the handshake?
   *SYN, SYN+ACK, ACK.*
5. What does a burst of lone SYNs to many ports suggest?
   *A port scan.*
