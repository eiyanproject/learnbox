---
title: "Domain 1: Design secure architectures"
summary: 30% of the exam. Identity and access across accounts, securing networks and workloads, and protecting data with encryption, keys and backups.
order: 1
kind: quiz
---

**Weight: 30% of the scored questions** - the largest domain. Three tasks:
secure access to AWS resources, secure workloads and applications, and data
security controls.

## Access

- **Root user**: MFA on, no access keys, used only for the few tasks that
  need it. Daily work happens as something else.
- **Least privilege**: policies grant named actions on named resources.
  Explicit **Deny** beats any Allow; anything not allowed is denied.
- **Roles over keys**: EC2 instance profiles, Lambda execution roles,
  cross-account roles. Temporary credentials from **STS** expire by
  themselves.
- **Cross-account**: a role in the target account trusting the other account;
  a third party gets an **external ID** condition (confused deputy).
- **People**: **IAM Identity Center** for single sign-on to many accounts,
  with permission sets, optionally federated to an existing directory.
  **Cognito** for the users of *your* application: user pools sign them in,
  identity pools hand out scoped AWS credentials.
- **Many accounts**: **AWS Organizations** groups accounts in OUs;
  **service control policies** cap what any principal in an account can do
  (they grant nothing). **Control Tower** sets up a governed landing zone with
  guardrails and account vending.
- **Permissions boundaries** cap what an identity can be given - the way to
  let developers create roles without escalating their own privileges.
- **Resource policies** (S3 bucket policies, KMS key policies, SQS queue
  policies) live on the resource and name a Principal.

## Workloads and networks

- **Security groups**: stateful, allow-only, attach to interfaces, can
  reference other groups. **Network ACLs**: stateless, ordered rules, can
  deny, subnet-wide; remember the ephemeral return ports.
- **Public subnet** = route to an internet gateway. Private subnets reach out
  through a **NAT gateway**; AWS services through **VPC endpoints** (gateway
  endpoints for S3 and DynamoDB, interface endpoints/PrivateLink for the rest).
- **WAF** filters HTTP (SQL injection, XSS, rate limits, IP sets) on
  CloudFront, ALB, API Gateway. **Shield Standard** is free DDoS protection;
  **Shield Advanced** adds a response team and cost protection.
- **GuardDuty** detects threats from logs; **Inspector** scans for
  vulnerabilities; **Macie** finds sensitive data in S3; **Security Hub**
  gathers findings.
- **Secrets Manager** stores and rotates secrets; **Parameter Store**
  SecureString is cheaper when rotation is not needed.
- Hybrid links: **Site-to-Site VPN** (quick, encrypted, over the internet),
  **Direct Connect** (private, consistent, takes weeks; add VPN or MACsec for
  encryption).

## Data

- **KMS**: customer managed keys for control, audit and key policies;
  automatic rotation. **SSE-S3**, **SSE-KMS**, **SSE-C**, client-side.
- **ACM** issues and renews TLS certificates for ALB, CloudFront, API
  Gateway; CloudFront certificates must be in **us-east-1**.
- S3: Block Public Access, TLS-only bucket policies, **Object Lock**
  (governance or compliance mode) for WORM retention, versioning, MFA delete.
- **AWS Backup** centralises backup plans, including cross-Region and
  cross-account copies.
- Shared responsibility: AWS secures the cloud (facilities, hardware,
  hypervisor); you secure what you put in it (guest OS, data, IAM, network
  configuration).

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 1; AWS service documentation.

## Questions from open banks

- 65 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
