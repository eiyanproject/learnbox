---
title: Network ACLs that deny
summary: Stateless subnet firewalls - numbered rules evaluated in order, the ephemeral ports replies need, and blocking an address range that security groups cannot.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws ec2 create-network-acl --vpc-id \"$VPC_ID\" --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=public}]' --query NetworkAcl.NetworkAclId --output text`."
  - "One entry per call: `aws ec2 create-network-acl-entry --network-acl-id \"$ACL\" --ingress --rule-number 100 --protocol tcp --port-range From=443,To=443 --cidr-block 0.0.0.0/0 --rule-action allow`. Outbound rules use `--egress`. The deny for every protocol is `--protocol -1` with no port range."
  - "Rules are evaluated lowest number first and the first match wins - so the deny for 198.51.100.0/24 needs a number below the allows (90, say)."
  - "A subnet is always associated with exactly one ACL, so you replace the association: find it with `aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=\"$PUBLIC_A\" --query \"NetworkAcls[0].Associations[?SubnetId=='$PUBLIC_A'].NetworkAclAssociationId\" --output text`, then `aws ec2 replace-network-acl-association --association-id \"$ASSOC\" --network-acl-id \"$ACL\"`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **network ACL** | access control list filtering traffic at a subnet's boundary |
| **rule number** | 1 to 32766; rules are checked lowest first |
| **first match wins** | the first rule that matches decides; later ones are never looked at |
| **final deny** | rule `*` (reported as 32767): denies anything nothing else matched; cannot be removed |
| **default ACL** | the VPC's own ACL: allows everything both ways |
| **custom ACL** | one you create: starts with only the final deny |
| **inbound (ingress)** / **outbound (egress)** | the two separate rule lists |
| **stateless** | does not know a packet is a reply; replies need their own rule |
| **packet** | one piece of network traffic |
| **ephemeral port** | a temporary high-numbered client port (1024-65535) that replies are sent to |
| **gaps in numbers** | numbering 90, 100, 110 so rules can be slotted in later |
| **association** | the link between a subnet and its one ACL; replaced, never added |
| **JMESPath filter** | `[?SubnetId=='...']`: keep only list items that match |
| **protocol `-1`** | all protocols |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws ec2 create-network-acl --vpc-id V` | creates a custom ACL |
| `aws ec2 create-network-acl-entry --network-acl-id A --ingress --rule-number 100 --protocol tcp --port-range From=443,To=443 --cidr-block C --rule-action allow` | adds one rule |
| `--ingress` / `--egress` | picks the inbound or outbound list |
| `aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=S` | finds the ACL a subnet uses |
| `aws ec2 replace-network-acl-association --association-id X --network-acl-id A` | moves the subnet to another ACL |

### Errors

| Error | Means |
|---|---|
| `NetworkAclEntryAlreadyExists` | two rules in the same direction with the same number |
| *(no error at all)* | ephemeral-port rules forgotten: everything looks allowed and nothing works |

---

Security groups only allow. Sometimes you need the opposite: an address
range is attacking your site, and you want it blocked for a whole subnet,
whatever any security group says. A **network ACL** (access control list)
can do that. It filters traffic at the boundary of a **subnet**: where a
security group wraps one network interface, an ACL covers everything in the
subnet, and it behaves quite differently:

| | Security group | Network ACL |
|---|---|---|
| Applies to | the interfaces it is attached to | every interface in the subnet |
| Rules | allow only | allow **and deny** |
| Evaluation | all rules together; any allow is enough | **in order of rule number**, lowest first; the first match wins |
| State | **stateful**: replies allowed automatically | **stateless**: replies need their own rule |
| Default | no inbound, all outbound | the VPC's default ACL allows everything |

Traffic entering an instance in a subnet passes both: first the subnet's ACL,
then the instance's security group. Either can stop it.

```text
 internet ──> [ network ACL of the subnet ] ──> [ security group of the instance ] ──> instance
```

## Rules, numbers and the final deny

Each ACL has two separate rule lists, **inbound** (ingress) and **outbound**
(egress). Each rule has a **number** from 1 to 32766, a protocol and port
range, an address range, and an action, `allow` or `deny`. For each packet,
AWS goes through the list in number order, and the **first** rule that
matches decides; later rules are never looked at.

The last rule, number `*`, denies everything that nothing before it
matched. It is always there and cannot be removed. Here is the VPC's
**default** ACL, which every new subnet uses: rule 100 allows everything, in
both directions (`True` is outbound), and the final rule, which the API
reports as 32767, denies the rest:

```
$ aws ec2 describe-network-acls --filters Name=default,Values=true \
    --query 'NetworkAcls[0].Entries[].[RuleNumber,Egress,Protocol,CidrBlock,RuleAction]' --output table
------------------------------------------------
|              DescribeNetworkAcls             |
+-------+--------+-----+-------------+---------+
|  100  |  True  |  -1 |  0.0.0.0/0  |  allow  |
|  32767|  True  |  -1 |  0.0.0.0/0  |  deny   |
|  100  |  False |  -1 |  0.0.0.0/0  |  allow  |
|  32767|  False |  -1 |  0.0.0.0/0  |  deny   |
+-------+--------+-----+-------------+---------+
```

Protocol `-1` means all protocols. A **custom** ACL, one you create, starts
with only the final deny, so it blocks everything until you add rules.

Number rules with gaps (90, 100, 110, ...), so a rule can be slotted in
between later without renumbering the rest. Two rules in the same direction
cannot share a number:
`NetworkAclEntryAlreadyExists ... The network acl entry identified by 100 already exists.`

Order is the whole game for a deny. With the deny at 90 and the HTTPS allow
at 100, a request from the blocked range matches 90 first and is denied. Put
the deny at 130 instead, and the same request matches the allow at 100 and is
let in; the deny is never reached.

## Ephemeral ports

Because an ACL is stateless, it does not know that a packet is a reply. A
reply is just another packet to filter, and it needs a rule of its own.

When a browser connects to your web server on port 443, the connection has
two ends: port 443 on the server, and an **ephemeral port** on the client,
a temporary high-numbered port the client's operating system picked for this
one connection. The server's replies are sent **to** that port. Most systems
pick from **1024-65535**. So a subnet serving HTTPS needs:

- inbound TCP **443** from the clients, and
- outbound TCP **1024-65535** to them, for the replies.

```text
 client 8.8.8.8:51234  ──request──>  server 10.0.1.5:443      inbound rule: TCP 443
 client 8.8.8.8:51234  <──reply────  server 10.0.1.5:443      outbound rule: TCP 1024-65535
```

The same holds the other way round: when an instance itself calls an HTTPS
service, the request goes **out** on 443 and the replies come **in** on an
ephemeral port, so that needs an outbound 443 and an inbound 1024-65535 rule.
Forgetting the ephemeral rules is the classic way to break a working site
with an ACL, and a classic exam question: everything looks allowed, and
nothing works.

Like security groups, network ACLs do not filter traffic to the VPC's DNS
resolver, DHCP, the instance metadata service or Time Sync. Each ACL holds
20 rules per direction by default (up to 40 on request), so ACLs suit a few
broad rules, not long lists of addresses.

## When to use one

Security groups do the everyday work. Reach for an ACL when you need to
**deny**: block a known bad address range for a whole subnet, or add a
coarse second layer that a mistaken security group cannot open.

## The commands

```
ACL=$(aws ec2 create-network-acl --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=public}]' \
  --query NetworkAcl.NetworkAclId --output text)
aws ec2 create-network-acl-entry --network-acl-id "$ACL" --ingress \
  --rule-number 100 --protocol tcp --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 --rule-action allow
```

One entry per call. `--ingress` or `--egress` picks the list; a rule for all
protocols is `--protocol -1`, with no `--port-range`.

A subnet is **always** associated with exactly one ACL (the default one,
until you change it), so you do not add an association, you **replace**
the existing one. That needs the current association's ID, which this
`--query` digs out of the ACL the subnet uses now:

```
ASSOC=$(aws ec2 describe-network-acls \
  --filters Name=association.subnet-id,Values="$PUBLIC_A" \
  --query "NetworkAcls[0].Associations[?SubnetId=='$PUBLIC_A'].NetworkAclAssociationId" \
  --output text)
aws ec2 replace-network-acl-association --association-id "$ASSOC" --network-acl-id "$ACL"
```

The `[?SubnetId=='...']` part is a JMESPath **filter**: of all the
associations of that ACL, keep the one for this subnet. The query uses
double quotes on the outside so the shell fills in `$PUBLIC_A`.

## Two more differences

Two more differences from security groups: an ACL does **not** filter
traffic between instances in the **same** subnet (it sits at the subnet's
edge), and because it is stateless, adding a deny rule **does** cut an open
connection at once, which removing a security group rule does not. An ACL
rule can only name address ranges, never security groups.

## Your task

On top of the Foundations VPC (`eval "$(awslab given vpc)"`, as before),
create an ACL named **`public`**, associated with **public-a and public-b**,
while the private subnets keep the default ACL. Give it these rules:

| Rule | Direction | Protocol / ports | Source / destination | Action |
|---|---|---|---|---|
| 90 | inbound | all | 198.51.100.0/24 | **deny** |
| 100 | inbound | TCP 443 | 0.0.0.0/0 | allow |
| 110 | inbound | TCP 22 | 203.0.113.0/24 | allow |
| 120 | inbound | TCP 1024-65535 | 0.0.0.0/0 | allow (replies to the instances' own outbound calls) |
| 100 | outbound | TCP 1024-65535 | 0.0.0.0/0 | allow (replies to clients) |
| 110 | outbound | TCP 443 | 0.0.0.0/0 | allow (the instances calling HTTPS services) |

The check does not only read the list: it works out what your ACL does
with sample packets, going through the rules in order as AWS would, so the
numbers matter. Among them:

| Packet | Should be |
|---|---|
| inbound TCP 443 from 8.8.8.8 (a customer) | allowed |
| inbound TCP 443 from 198.51.100.7 (the blocked range) | denied |
| inbound TCP 22 from 203.0.113.20 (the office) | allowed |
| inbound TCP 22 from 8.8.8.8 | denied |
| inbound TCP 80 (plain HTTP) from 8.8.8.8 | denied |
| inbound TCP 40000 from 8.8.8.8 (a reply to the instance's own call) | allowed |

and it requires the deny's number to be lower than every inbound allow.
After **Run**, `aws ec2 describe-network-acls --filters
Name=tag:Name,Values=public --output table` shows your rules as AWS stored
them.

## Check yourself

1. A network ACL allows inbound 443 but has no outbound rules. Does HTTPS
   work?
   *No: the replies to the clients' ephemeral ports are blocked.*
2. Deny at 130, allow 443 from anywhere at 100. Is the denied range
   blocked from HTTPS?
   *No: rule 100 matches first.*
3. How do you block one malicious address range for a whole subnet?
   *A low-numbered deny rule in the subnet's network ACL.*
4. What does a new custom network ACL allow?
   *Nothing, until you add rules; the VPC's default ACL allows everything.*
