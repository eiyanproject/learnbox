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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **firewall** | software that decides, for every packet, whether to let it through |
| **rule** | one line of a firewall: what to match, and what to do with a match |
| **action** | what a rule does: `allow` (accept) or `deny` (drop) |
| **match** | a rule applies to a packet when every field it names has the packet's value |
| **wildcard** ("any") | a field the rule leaves out, which matches every value |
| **protocol** (`proto`) | `tcp`, `udp` or `icmp` |
| **source** (`src`) | the address the packet comes from |
| **destination port** (`dst_port`) | the service the packet is trying to reach |
| **first match wins** | rules are checked in order and the first one that matches decides |
| **shadowed rule** | a rule that can never fire, because an earlier rule always catches its traffic first |
| **default** (policy) | what happens to a packet that no rule matched |
| **default deny** | refuse anything not explicitly allowed |
| **allow-list firewall** | explicit allows, ending in "deny everything else" |
| **CIDR range** | a block of addresses such as `10.0.0.0/8`; simplified to one address here |
| **stateful firewall** | one that remembers connections, so replies to allowed traffic get back in |
| **nftables** | the current Linux firewall; `iptables` is the older one |
| **security group** | a cloud provider's firewall, with the same logic |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sudo nft list ruleset` | shows the Linux firewall's current rules |
| `sudo nft -c -f file.nft` | checks a rules file for mistakes without applying it |
| `python firewall.py` | runs your program: evaluates two SSH packets |

### Python names

| Name | What it does |
|---|---|
| `FIELDS = ("proto", "src", "dst_port")` | given to you: the fields a rule may name |
| `rule.get(field)` | the rule's value for that field, or `None` if it does not name it |
| `wanted is not None and wanted != packet.get(field)` | the rule names this field, and the packet's value is different |
| `for rule in rules:` | each rule, in order |
| `return rule["action"]` | stops at the first match and gives its action |
| `default="deny"` | a parameter with a default value, used when the caller gives none |

---

A **firewall** decides, for every packet, whether to let it through. Beneath
the syntax of `nftables` or a cloud **security group**, the logic is a short,
ordered list of **rules** and two principles. Building that logic yourself is
the clearest way to understand what a firewall really does, and it is the
defensive capstone of this section.

## Rules

A rule says which packets it is about and what to do with them:

```text
allow  tcp  from 10.0.0.5  to port 22
```

"Allow TCP packets from 10.0.0.5 to port 22 (SSH)." A rule **matches** a
packet when every field it names has the packet's value. A field it leaves out
is a **wildcard**: it matches anything. So `allow tcp to port 443` matches
HTTPS from every address.

## Principle 1: first match wins

Rules are checked **in order**, and the first one that matches decides the
packet's fate. The rest are never looked at.

So order is meaning. A broad rule placed above a narrow one **shadows** it:

```text
deny   tcp  to port 22                 # matches every SSH packet...
allow  tcp  from 10.0.0.5 to port 22   # ...so this one can never fire
```

Swap the two lines and the admin at 10.0.0.5 can log in again. Rules that
never fire because an earlier one already caught their traffic are the most
common way a firewall ends up misconfigured.

## Principle 2: default deny

The most important rule is the one at the end that you do not write: what
happens to a packet **no** rule matched. The only safe answer is **deny**.

- With **default allow**, the firewall protects nothing the moment you forget
  a rule, and you will forget one. You find out when an attacker does.
- With **default deny**, a forgotten rule leaves you too locked down. Something
  stops working, you notice at once, and you add the missing `allow`.

So every well-built firewall is a list of explicit `allow`s ending in an
unwritten "deny everything else":

```text
allow tcp from 10.0.0.0/8 to port 22      # admin SSH
allow tcp from any        to port 443     # public HTTPS
# everything else: denied, without a rule saying so
```

## The same thing in nftables

Linux's firewall, **nftables**, writes exactly these ideas. In this ruleset,
`policy drop` is the default deny, and the rules are checked top to bottom:

```text
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    iif "lo" accept
    ip saddr 10.0.0.5 tcp dport 22 accept
    tcp dport 443 accept
  }
}
```

The first two lines are worth knowing. `ct state established,related accept`
makes it a **stateful** firewall: replies to connections this machine opened
are let back in. `iif "lo" accept` allows the machine to talk to itself. You
can list a machine's live rules with `sudo nft list ruleset`.

## Your turn

In `firewall.py`, a rule is a dict with an `action` plus any of `proto`,
`src` and `dst_port`. A missing field, or one set to `None`, means "any". A
packet is a dict with `proto`, `src` and `dst_port`. To keep it short, `src`
is one exact address rather than a range like `10.0.0.0/8`.

- `matches(rule, packet)`: does this rule apply to this packet?
- `evaluate(rules, packet, default="deny")`: the action of the first matching
  rule, or `default` if none match.

Run it: the admin's SSH packet is allowed, and the same packet from a stranger
is denied, although no rule says "deny".

```text
allow
deny
```

## Check yourself

1. Rule 1 denies all TCP to port 22; rule 2 allows SSH from 10.0.0.5. Can
   10.0.0.5 connect?
   *No: rule 1 matches first and shadows rule 2.*
2. What happens to a packet that no rule matches?
   *The default applies: deny.*
3. Why is default deny safer than default allow?
   *A forgotten rule then blocks something, which you notice, instead of
   opening something, which an attacker notices.*
4. What does a rule with no `src` field match?
   *Packets from any source.*
5. What does `policy drop` mean in nftables?
   *Default deny for that chain.*
