---
title: "Domain 5: Networking and content delivery"
summary: 18% of the exam. Configuring and connecting VPCs, DNS with Route 53 and its resolver, content delivery, and troubleshooting a path that does not work.
order: 5
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **egress-only internet gateway** | outbound-only IPv6; the IPv6 counterpart of a NAT gateway |
| **IPv6** | 128-bit addresses, all public |
| **gateway** / **interface endpoints** | private paths to AWS services |
| **VPC peering** | joins two VPCs; not transitive, no overlapping CIDRs |
| **Transit Gateway** | a hub for many VPCs and on-premises, with route tables per attachment |
| **attachment** | a VPC or VPN connected to a Transit Gateway |
| **segment** | keep groups of networks apart |
| **Site-to-Site VPN tunnels** | two per connection, in different AZs; configure both |
| **Direct Connect** | a private line to AWS |
| **AWS Network Firewall** | managed stateful firewall in the VPC, with intrusion prevention and domain filtering |
| **intrusion prevention** | blocking traffic that matches attack patterns |
| **domain filtering** | allow outbound only to listed domains |
| **Route 53 Resolver DNS Firewall** | blocks DNS lookups of bad domains from the VPC |
| **query logging** | records DNS queries |
| **Resolver inbound** / **outbound endpoint** | on-premises resolves AWS names / AWS resolves on-premises names, with **forwarding rules** |
| **invalidation**, **versioned file names** | fixes for stale CloudFront content |
| **Global Accelerator** | static anycast IPs, fast failover, TCP and UDP |
| **VPC Flow Logs** | each flow's addresses, ports and ACCEPT or REJECT |
| **Reachability Analyzer** | whether a path exists from A to B, and what blocks it, without sending traffic |
| **access logs** | per-request logs from ELB, WAF and CloudFront |
| **CloudWatch Network Monitor** | latency and packet loss to on-premises |
| **inbound ACCEPT, outbound REJECT** | the Flow Logs sign of a NACL missing its return rule |

---

Networking questions for operators are mostly "it doesn't connect, why?"
and "how do I connect these two?". Knowing which layer can block traffic
(route table, NACL, security group, firewall, DNS) and which tool shows it
is most of the work.

**Weight: 18% of the scored questions.**

## The VPC

*Practised in Networking lessons 1-2.*

- **Subnets**, **route tables**, **NACLs** (stateless, per subnet),
  **security groups** (stateful, per interface), **NAT gateways**
  (outbound for private IPv4 subnets), the **internet gateway**.
- An **egress-only internet gateway** is the IPv6 counterpart of a NAT
  gateway: outbound IPv6 only, nothing can start a connection inward.
  (IPv6 addresses are public, so a NAT gateway does not apply.)

## Private connectivity

*Practised in Networking lessons 3-4.*

| Connects | With |
|---|---|
| a VPC to AWS services, privately | **gateway endpoints** (S3, DynamoDB) and **interface endpoints** (PrivateLink) |
| two VPCs | **VPC peering** (not transitive, no overlapping CIDRs) |
| many VPCs and on-premises | **Transit Gateway**, with route tables per attachment to segment traffic |
| on-premises, over the internet | **Site-to-Site VPN**: each connection has **two tunnels**, in different AZs; use both |
| on-premises, privately | **Direct Connect** |

## Protection

- **Security groups** and **NACLs**.
- **AWS Network Firewall**: a managed, stateful firewall in the VPC, with
  intrusion prevention and **domain filtering** (allow outbound only to
  `*.example.com`).
- **Route 53 Resolver DNS Firewall**: blocks DNS lookups of bad or
  unapproved domains from the VPC.
- **WAF** for HTTP, **Shield** for DDoS.

## DNS

*Practised in Containers lesson 4.*

- Route 53 **routing policies** (simple, weighted, latency, failover,
  geolocation, geoproximity, multivalue, IP-based) and **health checks**.
- **Query logging** records the DNS queries from your VPCs or to your
  public zones.
- **Resolver endpoints** for hybrid DNS:

  | Endpoint | Direction |
  |---|---|
  | **Inbound** | on-premises servers resolve names in AWS (private hosted zones) |
  | **Outbound** + **forwarding rules** | resources in AWS resolve on-premises names (`corp.example.local`) |

## Content delivery

*Practised in Containers lesson 5.*

- **CloudFront**: cache policies and **TTLs**; stale content after an
  update is fixed with an **invalidation**, or avoided with **versioned
  file names**.
- **Global Accelerator**: static anycast IPs and fast failover, for TCP and
  UDP.

## Troubleshooting a path

| Tool | Shows |
|---|---|
| **VPC Flow Logs** | each flow's addresses, ports and **ACCEPT** or **REJECT**; a REJECT means a security group or NACL blocked it |
| **Reachability Analyzer** | whether a path exists from A to B, and **which component blocks it**, without sending traffic |
| ELB, WAF and CloudFront **access logs** | each request, its response and why it was blocked |
| **CloudWatch Network Monitor** | latency and packet loss to on-premises destinations |

A useful reading of Flow Logs: an inbound ACCEPT with an outbound REJECT
for the same connection points to a **NACL** (stateless, missing the return
rule); a security group would have allowed the reply.

| In a question | Answer |
|---|---|
| "outbound-only internet for IPv6" | egress-only internet gateway |
| "on-premises must resolve private hosted zone names" | Resolver inbound endpoint |
| "instances must resolve on-premises names" | Resolver outbound endpoint + forwarding rule |
| "allow outbound HTTPS only to approved domains" | AWS Network Firewall |
| "why can't A reach B?" | Reachability Analyzer |
| "users still see the old page after a deploy" | CloudFront invalidation, or versioned file names |

## Traps

- **Peering is not transitive**: A-B and B-C does not give A-C.
- A VPN connection's **two tunnels** are for redundancy: configure both.
- An **inbound** Resolver endpoint is for queries coming **in** from
  on-premises.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 5; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
