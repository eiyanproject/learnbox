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

A workstation was seen talking to an unfamiliar host, and a capture was taken.
Buried in it is an HTTP request uploading stolen data over plain HTTP - no TLS,
so the contents are right there for anyone who captured the traffic. This is the
network and forensics sections together: parse the capture, find the request,
read what left.

## The brief

`EXFIL` in `data.py` is a pcap. One of its packets is an HTTP `POST` whose body
carries a `secret=<value>` form field - the exfiltrated data. Recover that
value.

The frame layout is the one from the Network section: Ethernet, then IPv4, then
TCP, then the payload. The handshake packets carry no payload; the request does.
Once you have the payload bytes, the secret is an ordinary form field in the
body.

## Your turn

In `sniff.py`, write `find_exfil(pcap)` returning the exfiltrated secret value as
a string, or `None` if there is none.
