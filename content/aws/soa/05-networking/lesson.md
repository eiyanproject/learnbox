---
title: "Domain 5: Networking and content delivery"
summary: 18% of the exam. Configuring and connecting VPCs, DNS with Route 53 and its resolver, content delivery, and troubleshooting a path that does not work.
order: 5
kind: quiz
---

**Weight: 18% of the scored questions.**

- **VPC**: subnets, route tables, NACLs, security groups, NAT gateways,
  internet gateway, **egress-only internet gateway** (outbound-only IPv6).
- **Private connectivity**: gateway and interface endpoints (PrivateLink),
  peering, **Transit Gateway** (route tables per attachment), Site-to-Site
  VPN (two tunnels for redundancy), Direct Connect.
- **Protection**: Security groups, NACLs, **AWS Network Firewall**
  (stateful inspection, domain filtering), **Route 53 Resolver DNS
  Firewall**, WAF, Shield.
- **DNS**: Route 53 routing policies (simple, weighted, latency, failover,
  geolocation, geoproximity, multivalue, IP-based), health checks, **query
  logging**, **Resolver endpoints** - inbound (on-premises resolving AWS
  names) and outbound (AWS resolving on-premises names with forwarding
  rules).
- **Content delivery**: CloudFront (cache policies, TTLs, **invalidations**,
  versioned file names), Global Accelerator.
- **Troubleshooting**: **VPC Flow Logs** (ACCEPT/REJECT), **Reachability
  Analyzer** (is there a path from A to B, and what blocks it), ELB, WAF and
  CloudFront logs, CloudWatch Network Monitor.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 5; AWS service documentation.
