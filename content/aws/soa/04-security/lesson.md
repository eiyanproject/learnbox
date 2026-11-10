---
title: "Domain 4: Security and compliance"
summary: 16% of the exam. Running IAM day to day, finding out why access fails, multi-account guardrails, and the services that report findings - and acting on them.
order: 4
kind: quiz
---

**Weight: 16% of the scored questions.**

- **IAM in operation**: password policies, MFA, roles, federation,
  resource policies, **condition keys** (`aws:SourceIp`,
  `aws:RequestedRegion`, `aws:PrincipalOrgID`, `aws:MultiFactorAuthPresent`).
- **Troubleshooting access**: CloudTrail shows the denied call and who made
  it; the **IAM policy simulator** tests policies; **IAM Access Analyzer**
  finds resources shared outside the account or organization, and unused
  access.
- **Many accounts**: Organizations, **SCPs** (for example, deny everything
  outside approved Regions), IAM Identity Center.
- **Trusted Advisor** security checks: open security groups, exposed access
  keys, MFA on root, public snapshots.
- **Config** rules and **conformance packs**; **Security Hub** aggregates
  findings and checks standards across accounts; **GuardDuty** threat
  detection; **Inspector** vulnerability scanning of EC2, ECR images and
  Lambda; **Macie** for sensitive data in S3. EventBridge turns findings into
  automatic responses.
- **Data protection**: KMS key policies and grants, ACM renewal (DNS
  validation records must stay in place), Secrets Manager.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 4; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
