---
title: "Domain 1: Design secure architectures"
summary: 30% of the exam. Identity and access across accounts, securing networks and workloads, and protecting data with encryption, keys and backups.
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
| **SAA-C03** | the AWS Certified Solutions Architect - Associate exam |
| **domain** | one of the exam's four topic areas; this one is 30% of the scored questions |
| **qualifier** | the phrase that picks one answer: "MOST secure", "LEAST operational overhead" |
| **operational overhead** | the work of running something yourself |
| **scored** / **unscored questions** | 50 count, 15 do not, and you cannot tell which |
| **least privilege** | policies name only the actions and resources needed |
| **explicit Deny** | beats any Allow |
| **temporary credentials** | keys from STS that expire by themselves |
| **instance profile**, **execution role**, **task role** | how EC2, Lambda and ECS code get a role |
| **trust policy** | who may assume a role |
| **external ID** / **confused deputy** | a value a third party must present / tricking it into using your role |
| **IAM Identity Center** | single sign-on for staff to many accounts, with **permission sets** |
| **permission set** | the permissions a person gets in an account through Identity Center |
| **Active Directory** | Microsoft's company directory of users |
| **Cognito** | sign-in for your app's users: **user pools** sign in, **identity pools** give AWS credentials |
| **AWS Organizations**, **OU**, **SCP** | groups accounts; folders of accounts; maximum permissions that grant nothing |
| **Control Tower** | sets up a governed multi-account landing zone |
| **permissions boundary** | caps what an identity can ever be given |
| **resource policy** | a policy on a resource, naming a Principal |
| **security group** / **network ACL** | stateful, allow-only, per interface / stateless, can deny, per subnet |
| **ephemeral ports** | 1024-65535, where replies arrive |
| **gateway** / **interface endpoint** | free route-table path to S3 and DynamoDB / PrivateLink interface for other services |
| **Session Manager** | a shell with no open port, key pair or bastion |
| **AWS WAF** | filters HTTP requests: SQL injection, cross-site scripting, rate limits |
| **SQL injection**, **cross-site scripting** | attacks smuggling database commands / scripts into a web app |
| **Shield Standard** / **Advanced** | free DDoS protection / paid, with a response team and cost protection |
| **Firewall Manager** | applies WAF, Shield and security group rules across an organization |
| **GuardDuty** | finds threats from CloudTrail, VPC Flow Logs and DNS logs |
| **VPC Flow Logs** | records of network traffic in a VPC |
| **Inspector** | finds software vulnerabilities in EC2, ECR images and Lambda |
| **Macie** | finds sensitive data in S3 |
| **Security Hub** | gathers findings and checks standards such as CIS |
| **Detective** | helps investigate a finding |
| **Site-to-Site VPN** / **Direct Connect** | encrypted over the internet / private line, not encrypted by itself |
| **MACsec** | encryption on a Direct Connect link |
| **SSE-S3**, **SSE-KMS**, **DSSE-KMS**, **SSE-C**, **client-side** | the S3 encryption options |
| **ACM** | free public TLS certificates for ALB, CloudFront, API Gateway; CloudFront's must be in us-east-1 |
| **Object Lock** | WORM retention: **governance** mode can be overridden, **compliance** mode cannot |
| **WORM** | write once, read many |
| **AWS Backup** / **Vault Lock** | central backup plans / makes backups undeletable |
| **shared responsibility** | AWS secures the cloud; you secure what you put in it |
| **hypervisor** | the software that runs virtual machines on AWS's hardware |
| **management account** | the organization's paying account; SCPs never apply to it |

---

This page is a review of the first domain of the **AWS Certified Solutions
Architect - Associate** exam (SAA-C03), followed by practice questions. It
assumes the hands-on lessons; each section names the ones where you built
what it describes. Read a section, and when a term is unfamiliar, go back to
that lesson before doing the questions.

**Weight: 30% of the scored questions**, the largest domain. The exam guide
splits it into three tasks: secure **access** to AWS resources, secure
**workloads and applications**, and **data** security controls.

## How a question is built

Almost every question is a short story (what a company runs), a few
requirements (*must*, *needs*), and one **qualifier** at the end, such as
"MOST secure" or "LEAST operational overhead". Often two or three options
would work; the qualifier picks one. A way to work through them:

1. Read the last sentence first: find the qualifier.
2. Cross out every option that misses **any** requirement.
3. Cross out options that add work AWS already does for you (a custom
   script where a built-in feature exists).
4. Of what is left, pick the one that fits the qualifier.

| Qualifier | Usually wins | Usually loses |
|---|---|---|
| **MOST secure** | roles and temporary credentials, private subnets, VPC endpoints, least privilege | access keys, public IPs, open SSH, `*` in policies |
| **LEAST operational overhead** | managed, built-in features | scripts on EC2, cron jobs, self-managed software |
| **Prevent** something | SCPs, IAM denies, Object Lock, Block Public Access | detective tools alone |
| **Detect** or **audit** | CloudTrail, Config, GuardDuty, Macie | preventive tools alone |

The exam has 65 questions in 130 minutes (50 scored, 15 unscored that you
cannot tell apart), passes at 720 of 1000, and does not penalize wrong
answers: never leave one blank.

## Access

*Practised in Foundations lessons 1-4 and 8, Security lesson 3.*

- **The root user** is the email address that opened the account. It can do
  everything, including closing the account, and IAM policies cannot limit
  it. So: turn on **MFA**, create **no access keys** for it, lock the
  credentials away, and do daily work as something else. It cannot be
  deleted.
- **Least privilege** means policies name the actions and resources needed,
  nothing more. Evaluation is: anything not allowed is denied; an
  **explicit Deny** beats any Allow.
- **Roles over keys.** An access key is a long-lived password for the API;
  if it leaks, it works until someone notices. A **role** hands out
  **temporary credentials** from **STS** that expire by themselves. Code on
  EC2 gets a role through an **instance profile**, Lambda through its
  **execution role**, ECS tasks through a **task role**. "Store the keys in
  Secrets Manager" is still keeping long-lived keys.
- **Cross-account access**: a role in the account that owns the resources,
  whose **trust policy** names the other account. For a **third party**
  acting for you, add an **external ID** condition, against the **confused
  deputy** problem (the third party being tricked into using your role for
  someone else).
- **People** versus **your app's users**:

  | Who signs in | Service |
  |---|---|
  | your staff, to many AWS accounts | **IAM Identity Center**: single sign-on with **permission sets**, optionally from an existing directory (Active Directory, Okta, Entra ID) |
  | the customers of *your* application | **Cognito**: **user pools** sign them in (sign-up, MFA, social logins); **identity pools** exchange that sign-in for scoped AWS credentials |

- **Many accounts**: **AWS Organizations** groups accounts in **OUs**.
  **Service control policies** (SCPs) set the **maximum** permissions in the
  accounts below, even for their root users, and **grant nothing**. **Control
  Tower** sets up a governed multi-account **landing zone** with
  guardrails and an account factory.
- **Permissions boundaries** cap what an identity can ever be given. They
  are how you let developers create roles for their own applications without
  being able to create a role more powerful than themselves.
- **Resource policies** sit on the resource and name a **Principal**: S3
  bucket policies, KMS key policies, SQS queue policies, Secrets Manager
  resource policies. Across accounts, both the resource policy and the
  caller's own IAM policy must allow.

| In a question | Answer |
|---|---|
| "application on EC2 needs to read S3" | an IAM role through an instance profile |
| "no account may disable CloudTrail, even administrators" | an SCP denying the CloudTrail actions |
| "employees sign in once to all accounts" | IAM Identity Center |
| "mobile app users sign in and upload to S3" | Cognito user pool + identity pool |
| "a vendor's account needs access to ours" | a cross-account role with an external ID |
| "developers may create roles, but not escalate" | permissions boundaries |

## Workloads and networks

*Practised in Networking lessons 1-4, Foundations lesson 8.*

- **Security groups** are firewalls on network interfaces. They are
  **stateful** (a reply to an allowed request is allowed back
  automatically), contain **allow rules only**, and can name **another
  security group** as the source, for example "the database accepts 5432
  from the app's group". **Network ACLs** work per **subnet**, are
  **stateless** (return traffic needs its own rule, to the **ephemeral
  ports** 1024-65535), are evaluated in rule-number order, and **can deny**,
  which makes them the tool for blocking one IP range.
- A **public subnet** is one whose route table sends `0.0.0.0/0` to an
  **internet gateway**. Instances in **private subnets** reach out through
  a **NAT gateway** (outbound only), and reach AWS services privately
  through **VPC endpoints**: **gateway endpoints** (free, a route table
  entry) for S3 and DynamoDB; **interface endpoints** (PrivateLink, a
  network interface in your subnet, billed per hour) for the rest.
- Administration without SSH: **Session Manager** (Systems Manager) opens a
  shell through the agent, with no open port, no key pair and full logging.
- **Edge protection**:

  | Service | Does |
  |---|---|
  | **AWS WAF** | filters HTTP requests: SQL injection, cross-site scripting, rate limits, IP lists, countries. Attaches to CloudFront, ALB, API Gateway, AppSync, Cognito (not NLB). |
  | **Shield Standard** | free, automatic protection from common network-level DDoS attacks |
  | **Shield Advanced** | paid: a response team, cost protection against scaling bills from an attack, more visibility |
  | **Firewall Manager** | applies WAF, Shield and security group rules across all accounts of an organization |

- **Detection services**, often confused:

  | Service | Finds |
  |---|---|
  | **GuardDuty** | threats, from CloudTrail, VPC Flow Logs and DNS logs: crypto-mining, stolen credentials, calls from known bad IPs |
  | **Inspector** | software vulnerabilities (CVEs) in EC2, container images in ECR, Lambda |
  | **Macie** | sensitive data (personal data, credentials) in S3 |
  | **Security Hub** | gathers the other services' findings in one place, and checks accounts against security standards (CIS, AWS best practices) |
  | **Detective** | helps investigate a finding: what happened around it |

- **Secrets**: **Secrets Manager** stores secrets and **rotates** them;
  **Parameter Store** `SecureString` is cheaper when no rotation is needed
  (Security lesson 2).
- **Hybrid links**: **Site-to-Site VPN** is quick to set up, encrypted, over
  the internet. **Direct Connect** is a private, consistent connection that
  takes weeks to set up and is **not encrypted** by itself (add a VPN over
  it, or MACsec). A VPN is the usual backup for a Direct Connect link.

| In a question | Answer |
|---|---|
| "block one malicious IP range" | a network ACL deny (security groups cannot deny) |
| "only the app tier may reach the database" | the database's security group allowing the app's security group |
| "instances in private subnets need S3 without the internet" | an S3 gateway endpoint |
| "protect against SQL injection" | AWS WAF |
| "detect compromised instances / unusual API calls" | GuardDuty |
| "find credit card numbers in buckets" | Macie |
| "no SSH, no bastion, audited access" | Session Manager |

## Data

*Practised in Foundations lessons 5-6, Security lessons 1-2, Containers lesson 5.*

- **KMS** keys encrypt data at rest. A **customer managed key** gives you
  control: its own key policy, CloudTrail records of every use, rotation,
  sharing with other accounts. Encryption of S3 objects, one of:

  | Option | Key |
  |---|---|
  | **SSE-S3** | AWS manages it; the default for new objects |
  | **SSE-KMS** | a KMS key: access control and audit; **S3 Bucket Keys** cut the KMS request cost |
  | **DSSE-KMS** | two layers of KMS encryption, for rules that demand it |
  | **SSE-C** | you send your own key with every request; AWS never stores it |
  | **client-side** | you encrypt before upload; AWS never sees plaintext |

- **In transit**: TLS. **ACM** issues and renews public TLS certificates for
  free, for ALB, CloudFront and API Gateway (not for installing on EC2
  yourself). ❗ A certificate for **CloudFront** must be in **us-east-1**.
- **S3 protection**: **Block Public Access** on; a bucket policy denying
  requests without TLS (`aws:SecureTransport` false); **versioning** to
  recover overwritten or deleted objects; **Object Lock** for WORM (write
  once, read many) retention, in **governance** mode (special permission can
  override) or **compliance** mode (nobody, not even root, can delete before
  the date); MFA delete.
- **AWS Backup** runs backup plans across services (EBS, RDS, DynamoDB,
  EFS, S3...) centrally, including copies to other Regions and accounts.
  **Vault Lock** makes backups undeletable.
- **Shared responsibility**: AWS secures **the cloud** (buildings, hardware,
  the hypervisor, managed services' software); you secure what you put **in
  it**: the guest operating system, your data, IAM, network configuration,
  encryption choices. The more managed the service, the more moves to AWS.

| In a question | Answer |
|---|---|
| "control and audit who uses the encryption key" | SSE-KMS with a customer managed key |
| "keys must never be stored in AWS" | SSE-C or client-side encryption |
| "records must not be deleted for 7 years, by anyone" | S3 Object Lock in compliance mode |
| "force HTTPS for S3 access" | bucket policy deny when `aws:SecureTransport` is false |
| "central backups across services and accounts" | AWS Backup |

## Traps

- SCPs **never grant**: an SCP allowing S3 does not let anyone use S3.
- SCPs do **not** apply to the **management account**.
- A security group **cannot deny**; a NACL is **stateless**.
- **Direct Connect** alone is **not encrypted**.
- "Encrypt the access keys" or "rotate the keys" is still the wrong answer
  when a role is possible.
- Multi-AZ is about **availability**, not security; do not pick it for a
  security requirement.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 1; AWS service documentation.

## Questions from open banks

- 65 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
