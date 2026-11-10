---
title: "Domain 2: Design resilient architectures"
summary: 26% of the exam. Loose coupling and scaling, then high availability, failover and disaster recovery - what keeps working when part of it does not.
order: 2
kind: quiz
---

**Weight: 26% of the scored questions.** Two tasks: scalable, loosely
coupled architectures, and highly available or fault-tolerant ones.

## Loose coupling

- **SQS** puts a queue between producer and consumer, so a spike or a slow
  consumer does not break the producer. Standard queues: at-least-once,
  best-effort order. **FIFO** queues: exactly-once processing and order per
  **message group ID**. A **dead-letter queue** catches messages that keep
  failing (maxReceiveCount). If processing takes longer than the
  **visibility timeout**, the message reappears and is processed twice.
- **SNS** publishes one message to many subscribers; **SNS + SQS fan-out**
  gives each consumer its own queue.
- **EventBridge** routes events by rule from AWS services, SaaS and your own
  applications.
- **Step Functions** orchestrates multi-step workflows with retries, branches,
  waits and human approval.
- **API Gateway** fronts APIs with throttling, auth and caching; **Lambda**
  runs code per event; **ECS/EKS on Fargate** run containers without servers.
- Stateless tiers scale horizontally: keep **session state** out of the
  instance, in ElastiCache or DynamoDB.

## High availability

- Spread across **at least two Availability Zones**: an **ALB** in front of
  an **Auto Scaling group** that spans them; **RDS Multi-AZ** for a standby
  with automatic failover (a standby, not a read target - **read replicas**
  are for reads).
- **Aurora** keeps six copies of data across three AZs; **Aurora Global
  Database** replicates to other Regions with typically under a second of lag.
  **DynamoDB global tables** are multi-Region, multi-active.
- **Route 53** routing policies: failover (with health checks), latency,
  weighted, geolocation, geoproximity, multivalue.
- **RDS Proxy** pools database connections - for Lambda bursts and faster
  failover.
- **EFS** is a regional, multi-AZ shared file system for Linux; **FSx for
  Windows File Server** for SMB with Active Directory.
- **S3 Cross-Region Replication** (versioning on both sides) for copies in
  another Region.
- Plan **service quotas** in the standby Region before you need them.

## Disaster recovery

| Strategy | Running in the DR Region | RTO / RPO | Cost |
|---|---|---|---|
| Backup and restore | nothing but backups | hours / hours | lowest |
| Pilot light | data replicated, core idle or off | tens of minutes | low |
| Warm standby | scaled-down full copy, serving | minutes | higher |
| Multi-site active-active | full copy, serving | near zero | highest |

**RPO** is how much data you can lose; **RTO** how long you can be down.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 2; AWS whitepaper "Disaster Recovery of Workloads on AWS".

## Questions from open banks

- 60 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
