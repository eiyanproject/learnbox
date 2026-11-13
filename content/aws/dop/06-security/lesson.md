---
title: "Domain 6: Security and compliance"
summary: 17% of the exam. Identity and access at scale, security automation for data, networks and pipelines, and continuous compliance monitoring and auditing.
order: 6
kind: quiz
---

Security in DevOps is built into the pipeline and the platform, not
checked by hand afterwards: no long-lived keys anywhere, guardrails that
apply to every account, scanning in every build, and compliance monitored
continuously. The method for reading questions is on the Domain 1 page.

**Weight: 17% of the scored questions.**

## Identity and access

*Practised in Foundations lessons 3-4 and 8, Containers lessons 2-3.*

- **Roles everywhere**: instance profiles (EC2), task roles (ECS), **EKS Pod
  Identity** or **IRSA** (pods), and **OIDC federation** for CI systems
  outside AWS, such as GitHub Actions: the CI job presents a signed token,
  and STS exchanges it for a role's temporary credentials, so no access key
  is stored in the CI system. People use **IAM Identity Center**.
- **Least privilege at scale**:

  | Tool | Does |
  |---|---|
  | **permissions boundaries** | cap what delegated administrators can grant |
  | **SCPs** | cap what principals in member accounts can do |
  | **RCPs** (resource control policies) | cap what can be done **to resources** in member accounts, whoever asks, for example "no S3 access from outside the organization" |
  | **IAM Access Analyzer** | finds external sharing and **unused access**, **generates** policies from CloudTrail activity, and **checks custom policies** in a pipeline before they are deployed |

## Automating security controls

*Practised in Foundations lesson 6, Security lessons 1-2.*

- **Secrets Manager** with rotation; **KMS** key policies and grants.
- **Defaults**: S3 **Block Public Access at the account level**, **EBS
  default encryption** per Region, so nothing new is created unprotected.
- **Network**: security groups as code, **AWS Network Firewall**, and
  **Firewall Manager** applying WAF managed rules, security group policies
  and Network Firewall across all accounts, including new ones.
- **Pipeline security**:
  - scanning: **Inspector** for ECR images, Lambda functions and code
    repositories;
  - IaC checks: **cfn-guard** rules on templates, **CloudFormation Hooks**
    that block non-compliant resources;
  - **signed artifacts**, verified before deployment.

## Monitoring and audit

| Service | For |
|---|---|
| **Security Hub** | standards and controls across accounts, all findings in one place |
| **GuardDuty** | threat detection |
| **Inspector** | vulnerabilities |
| **Macie** | sensitive data in S3 |
| **Config** | conformance packs, aggregators |
| **CloudTrail** | API audit, with **log file validation** (a digest that proves the log files were not changed or deleted) |
| **Detective** | investigating a finding: what led to it |
| **Audit Manager** | collects **evidence** for audits against frameworks (PCI DSS, HIPAA, SOC 2) |

| In a question | Answer |
|---|---|
| "GitHub Actions deploys to AWS without stored keys" | OIDC federation to an IAM role |
| "no bucket in any account may be accessed from outside the org" | an RCP |
| "generate a least-privilege policy from what the role actually used" | IAM Access Analyzer policy generation |
| "block templates that create public buckets before deploy" | cfn-guard in the pipeline, or CloudFormation Hooks |
| "prove CloudTrail logs were not tampered with" | log file validation |
| "WAF rules on every account's ALBs, including new accounts" | Firewall Manager |
| "evidence for a PCI audit" | Audit Manager |

## Traps

- **SCPs** limit principals; **RCPs** limit resources. Neither grants.
- **Detective** investigates; it does not detect (GuardDuty does).
- Access keys in CI, even "rotated", lose to OIDC federation.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 6; AWS service documentation.

## Questions from open banks

- 3 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
