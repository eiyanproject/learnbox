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

Most network analysis is reading a **capture** - a file of recorded packets,
saved by `tcpdump -w` or Wireshark. The file format is `pcap`, and once you can
walk it you can answer the questions that matter: who talked to whom, on what
ports, and what was in the traffic.

## The pcap format

Simple by design:

- a **24-byte global header** (a magic number, version, and the link type)
- then, repeated to the end: a **16-byte record header** - timestamp and the
  captured length - followed by that many bytes of the raw frame

Each frame is the layering from the last lesson: Ethernet, then IP, then TCP,
then payload. Walking from the global header, record by record, gives you every
packet.

## The point: plain HTTP hides nothing

The sample capture is a client fetching a page over plain **HTTP** - no TLS. One
request carries an `Authorization: Basic` header, which is simply the username
and password base64-encoded. Base64 is not encryption (foundations lesson one),
so anyone who captured the traffic reads the credentials directly. This is the
original argument for HTTPS everywhere, and finding that credential in the
capture is the exercise.

A real analyst does this with Wireshark's "Follow TCP Stream" or `tshark -Y
http.authorization`; you are building the core of what those do, so the tools
stop being magic.

## Your turn

`SAMPLE` (a pcap as bytes) is provided in `capture_data.py`. In `capture.py`:

- `parse_pcap(data)` - the list of raw frames (bytes) in the capture
- `frame_endpoints(frame)` - `(src_ip, dst_ip, src_port, dst_port)` for a frame
- `frame_payload(frame)` - the bytes after the TCP header (may be empty)
- `find_basic_auth(frames)` - the decoded `user:pass` from an HTTP Basic auth
  header in any frame, or `None`
