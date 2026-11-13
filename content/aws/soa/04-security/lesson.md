---
title: "Domain 4: Security and compliance"
summary: 16% of the exam. Running IAM day to day, finding out why access fails, multi-account guardrails, and the services that report findings - and acting on them.
order: 4
kind: quiz
---

For an operations engineer, security is day-to-day work: answering "why
can't this role read that bucket?", keeping guardrails in place across
accounts, and acting on the findings that detection services report,
preferably automatically.

**Weight: 16% of the scored questions.**

## IAM in operation

*Practised in Foundations lessons 2-4.*

- Password policies, **MFA**, **roles**, federation, resource policies.
- **Condition keys** that appear often:

  | Key | Restricts by |
  |---|---|
  | `aws:SourceIp` | the caller's IP address (public IPs; not through VPC endpoints) |
  | `aws:RequestedRegion` | the Region the request goes to |
  | `aws:PrincipalOrgID` | membership of your organization: "any account in our org" without listing them |
  | `aws:MultiFactorAuthPresent` | whether the caller signed in with MFA |
  | `aws:SourceVpce` | the VPC endpoint the request came through |

## Finding out why access fails

| Tool | Answers |
|---|---|
| **CloudTrail** | which call was denied, who made it, from where (`errorCode: AccessDenied`) |
| **IAM policy simulator** | would these policies allow this action on this resource? |
| **IAM Access Analyzer** | which resources are shared **outside** the account or organization; which permissions are **unused**; and it checks policies as you write them |

Then work through the layers: identity policy, resource policy,
permissions boundary, SCP, session policy, and for KMS the key policy. An
explicit Deny anywhere wins.

## Many accounts

*Practised in Security lesson 3.*

- **Organizations** with **SCPs** as guardrails, for example denying
  everything outside approved Regions, or protecting CloudTrail.
- **IAM Identity Center** for people's access to every account.

## Checks and findings

| Service | Reports |
|---|---|
| **Trusted Advisor** | best-practice checks, including security: security groups open to the world, exposed access keys, MFA on root, public snapshots |
| **AWS Config** | resource configuration over time, and **rules** that mark resources compliant or not; **conformance packs** bundle rules; remediation through Automation runbooks |
| **Security Hub** | gathers findings and checks standards **across accounts** |
| **GuardDuty** | threats: compromised instances, unusual API calls, crypto-mining |
| **Inspector** | vulnerabilities in EC2, ECR images and Lambda |
| **Macie** | sensitive data in S3 |

**EventBridge** turns findings into responses: a GuardDuty finding starts a
Lambda function that isolates the instance; a Config non-compliant event
starts an Automation runbook that fixes the setting.

## Data protection

*Practised in Security lessons 1-2.*

- **KMS** key policies and grants (a key policy without the account
  delegation statement ignores IAM policies).
- **ACM** renews certificates automatically, with **DNS validation**, as
  long as the validation **CNAME record stays** in place; email-validated
  certificates need someone to click.
- **Secrets Manager** for credentials, with rotation.

| In a question | Answer |
|---|---|
| "who deleted the bucket?" | CloudTrail |
| "find buckets shared with other accounts" | IAM Access Analyzer |
| "allow access from any account in our organization" | `aws:PrincipalOrgID` in the resource policy |
| "mark unencrypted volumes and fix them automatically" | a Config rule with automatic remediation |
| "isolate an instance when GuardDuty reports it" | EventBridge rule on the finding, then Lambda or Automation |
| "ACM certificate did not renew" | the DNS validation record was removed |

## Traps

- Config **detects** and can remediate; it does not **prevent** (SCPs and
  IAM do).
- `aws:SourceIp` does not match traffic through a VPC endpoint: use
  `aws:SourceVpce` or `aws:SourceVpc`.
- Trusted Advisor's full set of checks needs a Business support plan or
  higher.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 4; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
