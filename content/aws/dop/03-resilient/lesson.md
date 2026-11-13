---
title: "Domain 3: Resilient cloud solutions"
summary: 15% of the exam. High availability across AZs and Regions, scaling that keeps up with demand, and automated recovery to meet RTO and RPO.
order: 3
kind: quiz
---

Resilience for a DevOps engineer is automated: instances replaced without a
person, capacity added before users notice, failover run by a runbook, and
experiments that prove all of it works. The method for reading questions is
on the Domain 1 page.

**Weight: 15% of the scored questions.**

## Highly available

*Practised in Compute lessons 2-3, Databases lessons 1-3.*

- **Across AZs**: Auto Scaling groups with **ELB health checks** (so a
  crashed application is replaced, not only a failed machine), Multi-AZ RDS
  and Aurora, EFS, DynamoDB. Remove **single points of failure**: one NAT
  gateway, one instance, one AZ.
- **Across Regions**: Route 53 health checks and **failover**, **Aurora
  Global Database**, **DynamoDB global tables**, S3 replication, ECR
  replication.

## Scalable

*Practised in Compute lesson 3, Containers lesson 2, Serverless lesson 3.*

- **Auto Scaling** policies: target tracking, step, **predictive** (learns
  daily and weekly patterns and scales ahead of them), scheduled; **warm
  pools** for slow-booting instances; **lifecycle hooks**.
- **ECS service auto scaling** through Application Auto Scaling.
- **Lambda concurrency**: reserved (guarantee and cap), provisioned
  (pre-initialized, no cold starts).
- **DynamoDB** on-demand or auto scaling; caching and read replicas;
  **queues** to absorb bursts.

## Automated recovery

- **Backups**: **AWS Backup** plans with cross-Region and cross-account
  copies, **Vault Lock**, point-in-time recovery, and **restore testing**
  (AWS Backup can restore on a schedule and check that the restore works).
- **Failover runbooks** in Systems Manager Automation or Step Functions,
  so a Regional failover is one tested procedure, not improvisation.
- **Application Recovery Controller** (ARC): readiness checks (is the
  standby really ready?), **routing controls** to move traffic between
  Regions reliably, and **zonal shift** to move traffic away from an
  impaired AZ.
- **Elastic Disaster Recovery** for continuous server replication.
- **AWS Fault Injection Service** (FIS) runs **chaos experiments**:
  terminate instances, add latency, fail an AZ, on purpose and with stop
  conditions, to prove the recovery works before a real failure does.

| In a question | Answer |
|---|---|
| "traffic peaks every weekday at 9:00; instances boot slowly" | predictive or scheduled scaling, plus a warm pool |
| "prove the backups can actually be restored" | AWS Backup restore testing |
| "move traffic away from an impaired AZ quickly" | ARC zonal shift |
| "verify the system survives an AZ loss" | an FIS experiment |
| "Regional failover must be one reliable, tested action" | ARC routing controls, or an Automation runbook |

## Traps

- Target tracking **reacts**; for a known peak with slow boots it is too
  late on its own.
- A backup that was never restored is not a tested backup.
- Reserved concurrency of 0 **stops** a function.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 3; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
