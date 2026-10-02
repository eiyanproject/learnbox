---
title: Firewall rules
summary: The section's defensive capstone - a rule engine with first-match evaluation and the default-deny posture that makes it safe.
order: 6
files: [firewall.py]
run: python firewall.py
hints:
  - "`matches`: a rule matches a packet when every field the rule specifies equals the packet's. A field set to `None` in the rule means 'any'."
  - "The fields are `proto`, `src` and `dst_port`."
  - "`evaluate`: walk the rules in order and return the action of the first that matches; if none match, return the `default`."
  - "`default` should be `'deny'` - anything not explicitly allowed is refused. That default-deny stance is what makes a firewall safe to get slightly wrong."
---

A firewall decides, for every packet, whether to let it through. Underneath the
`nftables` or cloud-security-group syntax, the logic is a short, ordered list of
rules and two principles. Building it is the clearest way to understand what a
firewall actually does - and it is the defensive capstone of this section.

## First match wins

Rules are evaluated **in order**, and the first one that matches decides the
packet's fate. Order is therefore meaning: a broad `deny` placed above a narrow
`allow` silently shadows it, and swapping two rules can open or close a service.
This is the most common way a firewall is misconfigured - a rule that never
fires because an earlier one already caught the traffic.

## Default deny

The rule that matters most is the one at the end that you do not write: what
happens to a packet no rule matched. The only safe answer is **deny**. A
firewall that allows by default protects nothing the moment you forget a rule -
and you will forget a rule. Default-deny means a mistake leaves you too locked
down (which you notice) rather than too open (which an attacker notices). Every
well-built firewall is a list of explicit `allow`s ending in an implicit "deny
everything else".

```text
allow tcp from 10.0.0.0/8 to port 22      # admin SSH
allow tcp from any        to port 443     # public HTTPS
# everything else: denied, without a rule saying so
```

## Your turn

In `firewall.py` (a rule is a dict with `action` plus any of `proto`, `src`,
`dst_port`; a missing or `None` field means "any". A packet is a dict with
`proto`, `src`, `dst_port`):

- `matches(rule, packet)` - does this rule apply to this packet?
- `evaluate(rules, packet, default="deny")` - the action of the first matching
  rule, or `default` if none match
