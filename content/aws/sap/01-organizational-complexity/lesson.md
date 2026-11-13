---
title: "Domain 1: Design solutions for organizational complexity"
summary: 26% of the exam. Networks spanning many VPCs, accounts and data centers, security controls across an organization, multi-account structure, resilience at scale, and cost visibility.
order: 1
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **SAP-C02** | the AWS Certified Solutions Architect - Professional exam |
| **constraint** | a requirement in the story: cost, overhead, time, compliance, minimal change |
| **Transit Gateway** | a Regional hub for VPCs, VPNs and Direct Connect |
| **mesh** | every network connected to every other directly |
| **route tables per attachment** | how a Transit Gateway segments traffic |
| **inter-Region peering** | connects Transit Gateways in different Regions |
| **Direct Connect gateway** | one Direct Connect connection reaching VPCs in many Regions |
| **VIF** | virtual interface: **transit VIF** to Transit Gateways, **private VIF** to virtual private gateways |
| **virtual private gateway** | a VPC's VPN and Direct Connect endpoint |
| **hybrid DNS** | Resolver inbound and outbound endpoints with forwarding rules |
| **AWS RAM** | shares resources, such as Resolver rules and subnets, with other accounts |
| **PrivateLink endpoint service** | one service exposed to many VPCs behind an NLB, even with overlapping CIDRs |
| **VPC sharing** | many accounts launching into subnets owned by a central network account |
| **SCP** | maximum permissions for accounts below; never grants |
| **tag policy**, **backup policy** | consistent tags / AWS Backup plans across accounts |
| **delegated administrator** | an account running a service, such as GuardDuty, for the whole organization |
| **Control Tower controls** | preventive (SCPs), detective (Config rules), proactive (CloudFormation hooks, before creation) |
| **Account Factory** | creates standard new accounts |
| **IAM Identity Center** | staff access to every account by group |
| **identity provider (IdP)** | the corporate system people sign in with |
| **SAML** / **SCIM** | standards for sign-in / for syncing users and groups |
| **log archive account** | receives the organization trail and Config history |
| **security tooling account** | delegated administrator for security services |
| **Config aggregator** | collects compliance from many accounts |
| **Elastic Disaster Recovery** | continuous block-level server replication, with failback |
| **failback** | returning to the original site after recovery |
| **Budgets actions** | apply an SCP or IAM policy when spending passes a limit |

---

This page reviews the first domain of the **AWS Certified Solutions
Architect - Professional** exam (SAP-C02), followed by practice questions.
The Professional exam assumes everything from the Associate one (the SAA
pages here) and adds scale: dozens of accounts, many VPCs, a data centre
that stays connected, and a company whose teams all need guardrails.

**Weight: 26% of the scored questions.**

## How a Professional question is built

The exam has 75 questions in 180 minutes and passes at 750 of 1000.
Questions are **long scenarios** with several options that would all work.
The right one meets **every** stated constraint best: cost, operational
overhead, time to deliver, compliance, minimal change. A way through:

1. Underline each constraint in the story, including the small ones ("the
   team has no Kubernetes experience", "within two weeks", "must not change
   the application").
2. Cross out options that break **any** constraint, however good otherwise.
3. Between the rest, the qualifier decides: least overhead favours managed
   services; cost favours what removes idle capacity; minimal change
   favours keeping protocols and engines.
4. Options often differ in one detail (a gateway endpoint against an
   interface endpoint, an SCP against an IAM policy); compare them side by
   side.

## Networks at scale

*Practised in Networking lessons 1-4.*

- **Transit Gateway** is a Regional hub that VPCs, VPNs and Direct Connect
  attach to, replacing a mesh of peering connections (with 20 VPCs, peering
  needs 190 connections; a Transit Gateway needs 20 attachments). Its
  **route tables per attachment** segment traffic: production VPCs and
  development VPCs share the hub but cannot reach each other.
  **Inter-Region peering** connects Transit Gateways in different Regions.
- **Direct Connect gateway**: one Direct Connect connection reaching VPCs
  in **many Regions**. A **transit VIF** (virtual interface) attaches it to
  Transit Gateways; a **private VIF** to virtual private gateways.
- **Hybrid DNS**: Route 53 Resolver **inbound** and **outbound** endpoints
  and **forwarding rules**, created once in a networking account and
  **shared** with every account through **AWS RAM**.
- **PrivateLink** exposes **one service** to many VPCs, even with
  **overlapping CIDRs**, without routing the networks together: consumers
  see an interface endpoint in their own VPC.
- **VPC sharing** (RAM) lets many accounts launch into **subnets owned by a
  central network account**: one VPC to manage, each account still owning
  its resources and bills.

| In a question | Answer |
|---|---|
| "connect 50 VPCs and the data centre, with segmentation" | Transit Gateway with separate route tables |
| "one Direct Connect, VPCs in three Regions" | Direct Connect gateway |
| "offer a service to customers' VPCs, CIDRs overlap" | PrivateLink (endpoint service behind an NLB) |
| "every account must resolve on-premises names" | Resolver outbound endpoint and rules shared with RAM |
| "central team manages the network, app teams own resources" | VPC sharing |

## Organization-wide control

*Practised in Security lesson 3, Operations lesson 2.*

- **Organizations**: OUs; **SCPs** as guardrails (they set the maximum,
  never grant); **tag policies** for consistent tags; **backup policies**
  for AWS Backup plans across accounts; **delegated administrators** so a
  security account runs GuardDuty or Config for everyone without using the
  management account.
- **Control Tower** sets up and governs it: a **landing zone**, **controls**
  (preventive as SCPs, detective as Config rules, **proactive** as
  CloudFormation hooks that check resources **before** they are created),
  and **Account Factory** for standard new accounts.
- **IAM Identity Center**, federated with the corporate identity provider
  over **SAML** for sign-in and **SCIM** to sync users and groups, gives
  staff access to every account by group.
- The usual structure: a **log archive** account receiving the
  **organization trail** of CloudTrail and Config history; a **security
  tooling** account as delegated administrator for GuardDuty, Security Hub
  and Config aggregators; workloads in their own accounts.

| In a question | Answer |
|---|---|
| "no account may leave approved Regions" | an SCP on the root or OU |
| "check resources before they are deployed" | Control Tower proactive controls (CloudFormation hooks) |
| "staff sign in with corporate credentials to all accounts" | Identity Center federated with the IdP (SAML + SCIM) |
| "logs must be kept where account admins cannot delete them" | organization trail to a separate log archive account |

## Resilience and cost at scale

- **DR** strategies (backup and restore, pilot light, warm standby,
  multi-site) as on the SAA Domain 2 page; **AWS Elastic Disaster
  Recovery** replicates servers continuously at block level, for recovery in
  minutes and failback afterwards.
- **Cost**: **consolidated billing**; cost allocation tags kept consistent
  by **tag policies**; **Cost Explorer**; **Budgets** with actions (apply an
  SCP or IAM policy when spending passes a limit); the Cost and Usage Report;
  **Savings Plans and Reserved Instances shared** across the organization's
  accounts (sharing can be turned off per account).

## Traps

- SCPs do not apply to the **management account**: keep workloads out of
  it.
- **Peering is not transitive**; Transit Gateway is the answer for many
  VPCs.
- PrivateLink shares a **service**, not a network.
- Detective controls report; they do not stop the action.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 1; AWS service documentation.

## Questions from open banks

- 4 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
