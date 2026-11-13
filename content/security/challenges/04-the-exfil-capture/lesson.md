---
title: "Challenge: the exfiltration on the wire"
summary: A packet capture of a host phoning home. Somewhere in it is the data that left - find it.
order: 4
files: [sniff.py]
run: python sniff.py
hints:
  - "Walk the pcap as in the network section: 24-byte global header, then 16-byte record headers and frames. The HTTP request is the frame with a payload."
  - "The secret is in the POST body, as a `secret=...` form field. Pull the payload out of the TCP segment and read the value."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **exfiltration** | data being copied out of an organisation by an attacker |
| **phoning home** | malware contacting the attacker's server |
| **packet capture** (pcap) | a file of recorded network packets (Network lesson 2) |
| **global header**, **record header** | the 24 bytes at the start of a pcap; the 16 bytes before each packet |
| **frame** | one recorded packet: Ethernet, then IPv4, then TCP, then the payload |
| **payload** | the data after the TCP header; empty for the handshake packets |
| **handshake** | the SYN, SYN+ACK, ACK packets that open a TCP connection |
| **plain HTTP** | HTTP without TLS, readable by anyone who records it |
| **`POST`** | the HTTP method for sending data to a server |
| **request body** | the part of an HTTP request after the blank line |
| **form field** | one `name=value` pair in a form body; pairs are joined with `&` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python sniff.py` | runs your program: prints the exfiltrated value |

### Python names

| Name | What it does |
|---|---|
| `EXFIL` | given to you in `data.py`: the capture, as bytes |
| `struct.unpack("<IIII", ...)` | a pcap record header: four little-endian 4-byte numbers |
| `(frame[14] & 0x0F) * 4` | the IPv4 header length in bytes |
| `(frame[tcp + 12] >> 4) * 4` | the TCP header length in bytes |
| `b"secret=" in payload` | `True` when those bytes appear |
| `.split(b"secret=", 1)[1]` | everything after the first `secret=` |
| `.split(b"&", 1)[0]` | everything before the next `&` |
| `.decode()` | bytes to text |

---

A workstation was seen talking to an unfamiliar server, and someone took a
**packet capture**. Inside it is an HTTP request uploading stolen data over
**plain HTTP**, with no TLS, so the contents are there for anyone who
recorded the traffic.

This challenge combines the Network and Forensics sections: parse the
capture, find the request, read what left.

## The brief

`EXFIL` in `data.py` is a pcap file. One of its packets is an HTTP `POST`
whose body carries a **form field** `secret=<value>`: the exfiltrated data.
Recover that value.

What you need from earlier lessons:

- **The file layout** (Network lesson 2): a 24-byte global header, then for
  each packet a 16-byte record header and the frame itself.
- **The frame layout** (Network lessons 1 and 2): Ethernet (14 bytes), then
  IPv4, then TCP, then the payload. The IP and TCP headers give their own
  lengths.
- **Which packet**: the handshake packets carry no payload; the request does.
- **The body** (Web lesson 1): after the headers and the blank line, form data
  looks like `name=value&name=value`.

## Your turn

In `sniff.py`, write `find_exfil(pcap)`. It returns the exfiltrated secret
value as a string, or `None` if there is none.

## Check yourself

1. Why can the secret be read from the capture at all?
   *It was sent over plain HTTP, without encryption.*
2. How do you tell the request packet from the handshake packets?
   *The handshake packets have an empty payload.*
3. In `user=bob&secret=abc&x=1`, where does the secret's value end?
   *At the next `&`.*
