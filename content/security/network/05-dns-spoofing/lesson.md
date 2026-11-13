---
title: DNS and spoofing
summary: How a name becomes an address, why an unauthenticated answer is forgeable, and the check that rejects a forged one.
order: 5
files: [dns.py]
run: python dns.py
hints:
  - "`parse_header`: the first 12 bytes are six big-endian 16-bit fields - id, flags, and the four counts. The response bit QR is the top bit of the flags field (`flags >> 15`)."
  - "A message is a response when the QR bit is 1."
  - "`accept_response`: only accept an answer that is actually a response AND whose (id, name) matches a query you recorded sending. Return its answer, else None."
  - "A forged answer arrives with an id you never used, or for a name you never asked about - either way it is not in your pending set."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **DNS** (Domain Name System) | the system that turns names like `example.com` into IP addresses |
| **domain name** | a human-readable name for a machine or service |
| **query** | the question: "what is the address of `example.com`?" |
| **response** (answer) | the reply, with the address |
| **resolver** | the server that looks names up for you, usually run by your network or ISP |
| **record** | one entry of DNS data; an **A record** maps a name to an IPv4 address |
| **UDP port 53** | where DNS queries usually go |
| **header** | the first 12 bytes of every DNS message |
| **transaction ID** | a 16-bit number in the query, which the response must repeat |
| **flags** | the second header field; its top bit is **QR** |
| **QR bit** | 0 in a query, 1 in a response |
| **question count**, **answer count** | how many questions and answers the message holds |
| **pending query** | one you sent and are still waiting to hear back about |
| **DNS spoofing** | sending a forged answer so that a name points to the attacker's address |
| **race** | the forged answer only works if it arrives before the real one |
| **cache** | answers a resolver remembers, so it does not ask again |
| **cache poisoning** | getting a forged answer stored in a resolver's cache, so everyone using it is misled |
| **source port randomisation** | sending each query from a random port, so a forger must guess the port too |
| **DNSSEC** | DNS records signed by their zone, so a validating resolver rejects forgeries |
| **zone** | the part of DNS one organisation controls, such as everything under `example.com` |
| **DNS over TLS / HTTPS** | encrypting the queries between you and your resolver |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dig example.com` | asks DNS for the name's address and shows the whole answer, including its ID and flags |
| `dig example.com +short` | shows just the address |
| `getent hosts example.com` | asks the system's own resolver, the way programs do |
| `python dns.py` | runs your program: parses a header and tests a real and a forged answer |

### Python names

| Name | What it does |
|---|---|
| `struct.unpack("!HHHHHH", data[:12])` | six 2-byte numbers, big-endian (`!`), from the first 12 bytes |
| `struct.pack("!HHHHHH", ...)` | the reverse: six numbers into 12 bytes |
| `flags >> 15 & 1` | the top bit of a 16-bit number: the QR bit |
| `bool(x)` | `True` for 1, `False` for 0 |
| `0x1234`, `0x8180` | numbers written in hex; `0x1234` is 4660 |
| `(ident, name) in pending` | `True` when that pair is one of the queries sent |
| `ident, name, is_response, answer_ip = response` | takes the tuple apart into four names |

---

**DNS** turns a name like `example.com` into an IP address. Your machine
sends a **query** to a **resolver**, and gets back a **response** with the
address. Almost everything you do online starts with a DNS lookup.

Like ARP, classic DNS has no authentication on the answer. Unlike ARP, the
attacker does not even need to be on your network.

## What a DNS message looks like

Every DNS message, query or response, starts with a 12-byte **header** of six
big-endian 16-bit fields:

| Field | Meaning |
|---|---|
| ID | the **transaction ID**: a 16-bit number chosen by the asker |
| flags | assorted bits; the top one, **QR**, is 0 in a query and 1 in a response |
| QDCOUNT | how many questions |
| ANCOUNT | how many answers |
| NSCOUNT, ARCOUNT | two more counts, not needed here |

```pycon
>>> import struct
>>> hdr = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0)
>>> from dns import parse_header
>>> parse_header(hdr)
{'id': 4660, 'is_response': True, 'questions': 1, 'answers': 1}
```

`0x8180` in binary starts with a 1, so this is a response. The response
**repeats the ID and the question** of the query it answers; that is how the
asker matches answers to questions.

## The forgery

DNS normally travels over UDP, which has no connection, so anyone who can send
a packet to your machine can send something that looks like an answer. To be
believed, a forged answer has to:

1. have the right **transaction ID**,
2. be for the **name** that was asked about, and
3. arrive **before** the real answer (a **race**).

If it succeeds, your machine uses the attacker's address for that name and
sends your traffic to them. That is **DNS spoofing**. When the forged answer
lands in a resolver's **cache**, it is **cache poisoning**, and everyone who
uses that resolver is sent to the wrong place until the entry expires.

## The defence in your code

What makes forgery hard is matching what you actually sent. So the defence is
to accept an answer **only** if it matches a query you really made:

- it must actually be a **response** (QR bit 1), not a stray query;
- its **(ID, name)** pair must match one of your **pending** queries.

A forged answer with an ID you never used, or for a name you never asked
about, is thrown away:

```text
pending: {(0x1234, "example.com")}
(0x1234, "example.com", response, 93.184.216.34)   -> accepted
(0x9999, "example.com", response, 6.6.6.6)         -> rejected: wrong ID
```

## The defence in the real world

A 16-bit ID has only 65,536 values, so a forger who can send many answers
quickly may guess it. Real resolvers therefore also use **source port
randomisation**: each query goes out from a random port, and the answer must
come back to that port. The forger now has to guess both, roughly 32 bits
instead of 16.

All of that makes forgery **harder**, not impossible. The fix that actually
**authenticates** answers is **DNSSEC**: each **zone** signs its records, and
a validating resolver rejects any answer whose signature does not check out.
It is the chain of trust from Crypto lesson 6, applied to DNS. Encrypted
transports, **DNS over TLS** or **over HTTPS**, also protect the step between
you and your resolver.

## Your turn

In `dns.py`:

- `parse_header(data)`: a dict `{id, is_response, questions, answers}` from
  the 12-byte header. `is_response` is a bool: the top bit of the flags field.
- `accept_response(pending, response)`: `pending` is a set of `(id, name)`
  queries you sent, and `response` is `(id, name, is_response, answer_ip)`.
  Return `answer_ip` if it is a response and matches a pending query;
  otherwise `None`.

Run it:

```text
{'id': 4660, 'is_response': True, 'questions': 1, 'answers': 1}
93.184.216.34
None
```

## Check yourself

1. What does the QR bit say?
   *Whether the message is a query (0) or a response (1).*
2. What must a forged answer get right to be believed?
   *The transaction ID and the name, and it must arrive first.*
3. What is cache poisoning?
   *A forged answer stored in a resolver's cache, misleading all its users.*
4. How does source port randomisation help?
   *The forger must guess the port as well as the ID.*
5. What actually authenticates DNS answers?
   *DNSSEC signatures.*
