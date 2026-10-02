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

**DNS** turns a name like `example.com` into an IP address. Your machine sends a
query to a resolver and gets back an answer. Like ARP, classic DNS has no
authentication on the answer - and unlike ARP, the attacker need not even be on
your network.

## The forgery

A query carries a 16-bit **transaction id** and the name asked about. The
resolver's reply echoes both. An attacker who can guess the id and get a forged
reply in **before** the real one wins - your machine caches the attacker's
address for the name and sends your traffic to them. This is **DNS spoofing**,
and when the bad answer is cached it becomes **cache poisoning**, affecting
everyone who uses that resolver.

What makes it hard for the attacker is matching what you actually sent: the right
transaction id, for the right name. The defence leans entirely on that - accept
an answer only if it matches a query you really made:

- it must actually be a **response**, not a stray query
- its **(id, name)** must match one you are waiting on

Real resolvers strengthen this by randomising the id *and* the source port,
turning a 16-bit guess into a 32-bit one - but the principle you implement is
the core: never accept an answer to a question you did not ask.

## Your turn

In `dns.py`:

- `parse_header(data)` - `{id, is_response, questions, answers}` from the 12-byte
  DNS header
- `accept_response(pending, response)` - given `pending`, a set of `(id, name)`
  queries you sent, and `response` as `(id, name, is_response, answer_ip)`,
  return `answer_ip` if it matches a pending query and is a response, else `None`
