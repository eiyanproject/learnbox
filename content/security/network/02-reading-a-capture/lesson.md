---
title: Reading a capture
summary: Parse a real pcap file, follow who talked to whom, and find the password that plain HTTP sent in the clear.
order: 2
files: [capture.py]
run: python capture.py
hints:
  - "A pcap starts with a 24-byte global header. After it, each packet is a 16-byte record header (little-endian `IIII`: seconds, microseconds, captured length, original length) followed by that many bytes of frame."
  - "`parse_pcap`: skip the 24-byte global header, then repeatedly read a 16-byte record header, take the captured-length bytes after it as one frame, and continue to the end."
  - "A frame is Ethernet (14 bytes) then IPv4 then TCP. Use the IP header length (low nibble of the byte at offset 14) to find where TCP starts, and the TCP data offset (high nibble of the byte at tcp+12) to find where the payload starts."
  - "`find_basic_auth`: look through the payloads for `Authorization: Basic `, take the token up to the next CRLF, and base64-decode it to `user:pass`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **capture** | a file of recorded network packets |
| **pcap** | the classic file format for captures, written by `tcpdump` and Wireshark |
| **global header** | the first 24 bytes of a pcap file: a magic number, the version and the link type |
| **magic number** | fixed first bytes that identify the format; for pcap, `d4 c3 b2 a1` |
| **record header** | 16 bytes before each packet: timestamp seconds, microseconds, captured length, original length |
| **captured length** | how many bytes of this packet were saved in the file |
| **original length** | how long the packet really was (it can be cut short when saved) |
| **little-endian** | least significant byte first; pcap's own headers use it |
| **big-endian** | most significant byte first; the packets inside use it |
| **frame** | one whole recorded packet, starting with its Ethernet header |
| **Ethernet header** | 14 bytes: destination MAC (6), source MAC (6), type (2) |
| **MAC address** | the hardware address of a network card, six bytes |
| **TCP data offset** | the high nibble of TCP byte 12: the TCP header length in 4-byte words |
| **endpoint** | one end of a conversation: an address and a port |
| **plain HTTP** | HTTP with no TLS: everything on the wire is readable |
| **Basic authentication** | sending `user:password`, base64-encoded, in an `Authorization` header |
| **in the clear** (cleartext) | readable by anyone who sees the traffic |
| **Follow TCP Stream** | Wireshark's view that joins a connection's payloads into one readable conversation |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `tcpdump -w file.pcap` | records packets into a capture file |
| `tcpdump -nn -r file.pcap` | reads a capture back, without turning addresses into names |
| `tshark -r file.pcap -Y http.authorization` | Wireshark's command-line form: shows only packets with that HTTP header |
| `python capture.py` | runs your program: lists the packets and the credentials found |

### Python names

| Name | What it does |
|---|---|
| `from capture_data import SAMPLE` | the lesson's capture, as bytes |
| `import struct` | loads the module that reads binary layouts |
| `struct.unpack("<IIII", data)` | four 4-byte unsigned numbers, little-endian (`<`) |
| `_, _, incl_len, _ = ...` | keeps only the third value; `_` means "not needed" |
| `offset += 16` | moves the reading position forward 16 bytes |
| `while offset + 16 <= len(data):` | keep going while a whole record header still fits |
| `frames.append(...)` | adds one frame to the list |
| `frame[26:30]` | the IP source address: 14 bytes of Ethernet plus 12 into IP |
| `(frame[tcp + 12] >> 4) * 4` | the TCP header length in bytes |
| `marker in payload` | `True` when those bytes appear in the payload |
| `payload.split(marker, 1)[1]` | everything after the first `marker` |
| `.split(b"\r\n", 1)[0]` | everything before the next line ending |
| `base64.b64decode(token).decode()` | the token decoded from base64, then turned from bytes into text |

---

Most network analysis means reading a **capture**: a file of recorded
packets, saved by `tcpdump -w` or Wireshark. The usual format is **pcap**.
Once you can walk through one, you can answer the questions that matter: who
talked to whom, on which ports, and what was in the traffic.

## The pcap format

It is simple by design:

```text
[ global header, 24 bytes ]
[ record header, 16 bytes ][ frame ... ]
[ record header, 16 bytes ][ frame ... ]
...to the end of the file
```

- The **global header** starts with the **magic number** `d4 c3 b2 a1` and
  also gives the version and the kind of link (Ethernet here).
- Each **record header** is four 4-byte unsigned numbers: the timestamp in
  seconds, the microseconds, the **captured length** and the original length.
- Then come captured-length bytes of the raw **frame**.

```pycon
>>> from capture_data import SAMPLE
>>> SAMPLE[:4].hex()          # the pcap magic number
'd4c3b2a1'
>>> import struct
>>> struct.unpack("<IIII", SAMPLE[24:40])   # the first record header
(1000, 0, 54, 54)
```

The first packet was recorded at second 1000, and 54 bytes of it are saved.

Unlike the packets inside them, the pcap headers are **little-endian** (least
significant byte first), so `struct` reads them with `"<IIII"`: `<` for
little-endian, `I` for a 4-byte unsigned number. The file format was designed
for the machines that wrote it, not for the network.

To walk the file: start at byte 24, read a record header, take the next
captured-length bytes as one frame, move on, and repeat until the end.

## Inside a frame

Each frame is the layering from Network lesson 1, with Ethernet in front:

| Part | Size | Notes |
|---|---|---|
| Ethernet | 14 bytes | destination MAC (6), source MAC (6), type (2) |
| IP | usually 20 bytes | length in the low nibble of its first byte, frame byte 14 |
| TCP | usually 20 bytes | length in the high nibble of its byte 12, in 4-byte words |
| payload | the rest | here, an HTTP request |

So the IP source address is at frame bytes 26 to 29 (14 for Ethernet, plus
12), and the destination at 30 to 33. The TCP header starts at
`14 + IP length`, and the payload at `TCP start + TCP length`.

## The point: plain HTTP hides nothing

The sample capture is a client fetching a page over **plain HTTP**, with no
TLS. The client sends a username and password using **Basic
authentication**: an `Authorization: Basic` header holding `user:password`,
base64-encoded. Base64 is an encoding, not encryption (Foundations lesson 1),
so anyone who captured the traffic can read the credentials straight off.

That is the original argument for HTTPS everywhere. Finding that password in
the capture is the exercise.

An analyst would do this with Wireshark's "Follow TCP Stream", or with
`tshark -r file.pcap -Y http.authorization`. You are building the core of
what those tools do, so that they stop being magic.

## Your turn

`SAMPLE` (a pcap file, as bytes) is given to you in `capture_data.py`. In
`capture.py`:

- `parse_pcap(data)`: the list of raw frames (bytes) in the capture.
- `frame_endpoints(frame)`: `(src_ip, dst_ip, src_port, dst_port)` for a
  frame.
- `frame_payload(frame)`: the bytes after the TCP header (may be empty).
- `find_basic_auth(frames)`: for the first frame whose payload contains
  `Authorization: Basic `, take the base64 token after it, up to the `\r\n`
  that ends the header line, and return it decoded to the string
  `user:pass`. Return `None` if no frame has one.

Run it:

```text
3 packets
('192.168.0.50', '93.184.216.34', 51000, 80)
('93.184.216.34', '192.168.0.50', 80, 51000)
('192.168.0.50', '93.184.216.34', 51000, 80)
credentials in the clear: admin:s3cret
```

## Check yourself

1. What comes before every packet in a pcap file?
   *A 16-byte record header with the timestamp and lengths.*
2. Why `"<IIII"` and not `"!IIII"` for that header?
   *pcap's own headers are little-endian; only the packets are big-endian.*
3. At which byte of a frame does the IP header start?
   *14, after the Ethernet header.*
4. Why can anyone read a Basic authentication password from a capture of
   plain HTTP?
   *It is only base64-encoded, and nothing encrypts the traffic.*
5. What fixes that?
   *HTTPS: TLS encrypts the whole request.*
