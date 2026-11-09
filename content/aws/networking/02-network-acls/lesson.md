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

A **network ACL** filters traffic at the boundary of a subnet. Where a
security group wraps one network interface, an ACL covers everything in the
subnet - and it behaves quite differently:

| | Security group | Network ACL |
|---|---|---|
| Applies to | interfaces it is attached to | every interface in the subnet |
| Rules | allow only | allow **and deny** |
| Evaluation | all rules together | **in order of rule number**, first match wins |
| State | **stateful**: replies allowed automatically | **stateless**: replies need their own rule |

Every VPC has a **default** ACL that allows everything in and out, and new
subnets use it. A **custom** ACL starts by denying everything (the final `*`
rule), so you add what is needed.

## Ephemeral ports

Because an ACL is stateless, a reply is just another packet to filter. When
a browser connects to your web server on 443, the server replies to the
browser's **ephemeral port** - a random high port the client chose, in the
range **1024-65535** for most systems. So a subnet serving HTTPS needs:

- inbound TCP 443 from the clients, and
- **outbound TCP 1024-65535** to them for the replies.

Forgetting the outbound ephemeral rule is the classic way to break a site
with an ACL - and a classic exam question.

## When to use one

Security groups do the everyday work. Reach for an ACL when you need to
**deny**: block a known bad address range for a whole subnet, or add a
coarse second layer that a mistaken security group cannot open.

## Your task

On top of the foundations VPC, create an ACL named **`public`** for the
public subnets, associated with **public-a and public-b**, with these rules:

| Rule | Direction | Protocol / ports | Source / destination | Action |
|---|---|---|---|---|
| 90 | inbound | all | 198.51.100.0/24 | **deny** |
| 100 | inbound | TCP 443 | 0.0.0.0/0 | allow |
| 110 | inbound | TCP 22 | 203.0.113.0/24 | allow |
| 120 | inbound | TCP 1024-65535 | 0.0.0.0/0 | allow (replies to the instances' own outbound calls) |
| 100 | outbound | TCP 1024-65535 | 0.0.0.0/0 | allow (replies to clients) |
| 110 | outbound | TCP 443 | 0.0.0.0/0 | allow (the instances calling HTTPS services) |

The check works out, for sample packets, what your ACL would do - so it
cares about the order, not just the list.
