---
title: "Domain 1: Design solutions for organizational complexity"
summary: 26% of the exam. Networks spanning many VPCs, accounts and data centers, security controls across an organization, multi-account structure, resilience at scale, and cost visibility.
order: 1
kind: quiz
---

**Weight: 26% of the scored questions.** Professional questions are long
scenarios with several workable answers; the right one meets *every* stated
constraint (cost, operational overhead, time, compliance) best.

## Networks at scale

- **Transit Gateway**: hub for many VPCs and VPNs/Direct Connect, with route
  tables per attachment for segmentation; **inter-Region peering** between
  Transit Gateways. **Direct Connect gateway** reaches VPCs in many Regions
  over one connection; a **transit VIF** attaches it to Transit Gateways.
- **Hybrid DNS**: Route 53 Resolver inbound and outbound endpoints and
  rules, shared across accounts with **AWS RAM**.
- **PrivateLink** exposes a service to many VPCs (even with overlapping
  CIDRs) without routing between them.
- **VPC sharing** (RAM) puts many accounts' workloads in centrally managed
  subnets.

## Organization-wide control

- **Organizations**: OUs, **SCPs** (guardrails, never grants),
  **tag policies**, **backup policies**, delegated administrators.
- **Control Tower**: landing zone, controls (preventive, detective,
  proactive), Account Factory.
- **IAM Identity Center** federated with the corporate IdP (SAML/SCIM).
- Centralized logging account (CloudTrail organization trail), security
  tooling account (GuardDuty, Security Hub, Config aggregators as delegated
  admins).

## Resilience and cost at scale

- DR: backup/restore, pilot light, warm standby, multi-site; **AWS Elastic
  Disaster Recovery** for continuous block-level replication of servers.
- Cost: **consolidated billing**, cost allocation tags enforced by tag
  policies, **Cost Explorer**, **Budgets** with actions, CUR, **Savings
  Plans and RI sharing** across the organization.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 1; AWS service documentation.

## Questions from open banks

- 4 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
