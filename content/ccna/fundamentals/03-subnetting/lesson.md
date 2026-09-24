---
title: Subnetting without a calculator
summary: Masks, network and broadcast addresses, usable host counts, and splitting a block - the arithmetic the exam tests under time pressure.
order: 3
files: [subnetting.py]
run: python -i subnetting.py
hints:
  - "`ipaddress` does the heavy lifting: `ipaddress.ip_network(f\"{ip}/{mask}\", strict=False)` accepts a dotted mask and gives you `.network_address`, `.broadcast_address` and `.prefixlen`."
  - "`usable_hosts`: 2 ** (32 - prefix) - 2, because the network and broadcast addresses are not usable. The exception is /31 (point to point, 2 usable) and /32 (1), which the tests check."
  - "`same_subnet` is the calculation a host does before every packet: put both addresses through the same mask and compare the results."
  - "`split` is `list(ipaddress.ip_network(cidr).subnets(new_prefix=n))` - return them as strings so they compare cleanly."
---

Subnetting is the part of CCNA people fail on time rather than understanding.
The arithmetic is small; doing it in your head, reliably, under pressure, is
the skill.

## The mask is a boundary, not a number

An address is 32 bits. The mask says where the network part stops:

```
192.168.1.10     11000000.10101000.00000001.00001010
255.255.255.0    11111111.11111111.11111111.00000000
                 |------ network ---------|- host -|
```

AND them together and you get the **network address**: 192.168.1.0. Set every
host bit to 1 and you get the **broadcast address**: 192.168.1.255. Neither is
usable by a host, which is where the "minus 2" comes from.

| Prefix | Mask | Usable hosts |
|---|---|---|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /27 | 255.255.255.224 | 30 |
| /28 | 255.255.255.240 | 14 |
| /30 | 255.255.255.252 | 2 |

Learn the last octet values — 128, 192, 224, 240, 248, 252 — and most questions
become one subtraction.

## Two exceptions worth knowing

- **/31** has no network or broadcast address by convention; both addresses are
  usable, which is why it is used for router-to-router links.
- **/32** is a single host, used for loopbacks.

The "minus 2" rule does not apply to either, and the exam has been known to ask.

## The calculation a host does

Before sending any packet, a host compares its own network address with the
destination's, using **its own** mask:

```
192.168.1.10  /24  ->  192.168.1.0
192.168.1.99  /24  ->  192.168.1.0     same subnet, send directly
192.168.2.10  /24  ->  192.168.2.0     different, send to the gateway
```

Get the mask wrong on one host and it will reach some destinations and not
others, which looks like a routing problem and is not.

## Splitting a block

Given 192.168.1.0/24 and a need for four networks, borrow two host bits — /26 —
and you get 192.168.1.0/26, .64/26, .128/26, .192/26. Borrowing *n* bits gives
2ⁿ subnets, each with a quarter of the addresses each time you borrow one more.

## Your turn

In `subnetting.py`:

- `network_address(ip, mask)`: the network address as a string
- `broadcast_address(ip, mask)`: the broadcast address as a string
- `usable_hosts(prefix)`: how many addresses a host can actually use, handling
  /31 and /32 correctly
- `same_subnet(a, b, mask)`: whether two addresses share a subnet under a mask
- `split(cidr, new_prefix)`: the list of subnets, as strings like
  `"192.168.1.0/26"`
