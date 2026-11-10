---
title: "Domain 6: Security and compliance"
summary: 17% of the exam. Identity and access at scale, security automation for data, networks and pipelines, and continuous compliance monitoring and auditing.
order: 6
kind: quiz
---

**Weight: 17% of the scored questions.**

## Identity and access

- Roles everywhere: instance profiles, task roles, IRSA and **EKS Pod
  Identity**, OIDC federation for CI systems outside AWS (for example GitHub
  Actions) instead of access keys, IAM Identity Center for people.
- Least privilege: permissions boundaries, SCPs and RCPs, IAM Access
  Analyzer (unused access, policy generation, custom policy checks in
  pipelines).

## Automating security controls

- Secrets in Secrets Manager with rotation; KMS key policies and grants;
  S3 Block Public Access at account level; encryption by default (EBS
  default encryption).
- Network: security groups as code, AWS Network Firewall, WAF managed
  rules via **Firewall Manager** across accounts.
- Pipeline security: scanning code and images (Inspector for ECR images,
  Lambda and code repositories), IaC checks (cfn-guard, Hooks), signed
  artifacts.

## Monitoring and audit

- **Security Hub** standards and controls, **GuardDuty**, **Inspector**,
  **Macie**, **Config** conformance packs with aggregators, **CloudTrail**
  with log file validation, **Detective** for investigation, **Audit
  Manager** for evidence.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 6; AWS service documentation.
