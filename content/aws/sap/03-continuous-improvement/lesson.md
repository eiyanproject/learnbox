---
title: "Domain 3: Continuous improvement for existing solutions"
summary: 25% of the exam. Take a running workload and make it more operable, secure, performant, reliable and cheaper, usually under constraints like no downtime or minimal change.
order: 3
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **smallest change** | the fix that solves the stated problem without breaking other constraints |
| **observability** | metrics, logs, alarms and traces |
| **Contributor Insights** | the top contributors in logs: which IPs, which keys |
| **X-Ray** | request traces |
| **CloudWatch Synthetics canary** | a script testing an endpoint or user journey every few minutes |
| **Patch Manager**, **Automation**, **State Manager** | Systems Manager automation features |
| **automatic remediation** | Config rules that fix what they find |
| **change sets**, **drift detection** | safe CloudFormation changes |
| **IAM Roles Anywhere** | temporary credentials for servers outside AWS, using X.509 certificates |
| **X.509 certificate** | a standard certificate proving a machine's identity |
| **S3 Batch Operations** | runs one action, such as an encrypting copy, over millions of objects |
| **encrypted snapshot copy** | how an unencrypted RDS database becomes encrypted: copy, restore, switch over |
| **bottleneck** | the part that limits the whole system |
| **gp3**, **io2**, **RDS Proxy**, **read replicas**, **caching** | fixes for what the metrics show |
| **right-size**, **Compute Optimizer**, **Savings Plans**, **Graviton** | cost improvements; commit after right-sizing |
| **Cost Optimization Hub**, **Trusted Advisor** | list idle resources and savings |
| **microservices** | an application split into small independent services |

---

In this domain the system is already in production, and something about
it is not good enough: too slow, too fragile, too expensive, not secure
enough, too much manual work. Look for the **smallest change** that fixes
the stated problem without breaking the other constraints, often "no
downtime" or "minimal changes to the application". The method for reading
questions is on the Domain 1 page.

**Weight: 25% of the scored questions.**

## Operational excellence

*Practised in Operations lessons 1-3.*

- **Observability**: CloudWatch metrics, logs and alarms;
  **Contributor Insights** (the top contributors in logs: which IPs, which
  keys); **X-Ray** traces; **CloudWatch Synthetics canaries**, scripts that
  test an endpoint or user journey every few minutes, so you hear about a
  broken login before customers do.
- **Automation** instead of manual steps: Systems Manager (**Patch
  Manager**, **Automation** runbooks, **State Manager**), EventBridge-driven
  remediation, **Config rules with automatic remediation**.
- **Safe changes**: CloudFormation **change sets** and **drift detection**;
  canary deployments with automatic rollback.

## Security improvements

*Practised in Foundations lessons 4-8, Security lessons 1-2.*

- **Remove long-lived keys**: roles for AWS workloads, **IAM Roles
  Anywhere** for servers **outside** AWS (they get temporary credentials
  using X.509 certificates), Identity Center for people.
- **Rotate secrets** with Secrets Manager.
- **Encrypt existing data**: default encryption only affects **new**
  objects, so existing S3 objects need **S3 Batch Operations** to copy them
  in place; an unencrypted RDS database cannot be encrypted in place, so
  **copy a snapshot with encryption on and restore** a new instance from it.
- Turn on **GuardDuty**, **Inspector**, **Macie**, and **Security Hub**
  controls.

## Performance and reliability

- Fix the **bottleneck the metrics show**, not a guess:

  | Metric shows | Fix |
  |---|---|
  | the same reads hit the database | caching: CloudFront, ElastiCache, DAX |
  | read load high, writes fine | read replicas |
  | connection count spikes (Lambda) | RDS Proxy |
  | volume IOPS or throughput at its limit | gp3 with more IOPS, or io2 |
  | spikes overload a backend | an SQS queue to absorb them |
  | an AZ failure took it down | Multi-AZ, Auto Scaling across AZs |
  | crashed apps stay in service | ELB health checks on the Auto Scaling group |

## Cost

- **Right-size** with **Compute Optimizer**; buy **Savings Plans** for the
  steady baseline that remains; **Spot** for interruptible work;
  **Graviton**; **storage lifecycle** rules; delete idle resources
  (**Trusted Advisor**, **Cost Optimization Hub**); cut **data transfer**
  (endpoints, same-AZ traffic, CloudFront).

| In a question | Answer |
|---|---|
| "on-premises servers use access keys to call AWS" | IAM Roles Anywhere |
| "encrypt millions of existing S3 objects" | S3 Batch Operations copy with encryption |
| "encrypt an existing RDS database" | encrypted snapshot copy, restore, switch over |
| "detect a broken checkout flow before users do" | CloudWatch Synthetics canary |
| "high NAT costs for S3 traffic" | an S3 gateway endpoint |

## Traps

- "Rebuild it as microservices" is rarely the smallest change.
- Default encryption does not encrypt objects already stored.
- Commit to Savings Plans **after** right-sizing, not before.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 3; AWS service documentation.

## Questions from open banks

- 4 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
