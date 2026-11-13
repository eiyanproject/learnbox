---
title: "Domain 4: Accelerate workload migration and modernization"
summary: 20% of the exam. Assess a portfolio, pick a migration strategy per workload, move data and servers with the right tools, and modernize once in AWS.
order: 4
kind: quiz
---

A company is moving to AWS: hundreds of applications, servers and
databases, each needing its own decision. This domain is about assessing
that portfolio, picking a **strategy** per workload, moving servers and
data with the right **tool**, and modernizing afterwards. The method for
reading questions is on the Domain 1 page.

**Weight: 20% of the scored questions.**

## Assess and plan

- **The 7 Rs**, one per workload:

  | Strategy | Means | Example |
  |---|---|---|
  | **Retire** | switch it off | an app nobody uses |
  | **Retain** | leave it where it is, for now | recently upgraded, or not ready |
  | **Rehost** | lift and shift, unchanged, to EC2 | fastest move, with MGN |
  | **Relocate** | move the platform as it is | VMware VMs to VMware Cloud on AWS |
  | **Repurchase** | replace with SaaS | an in-house CRM to a SaaS CRM |
  | **Replatform** | lift, tinker and shift | self-managed database to RDS |
  | **Refactor** | re-architect for the cloud | monolith to serverless |

  The exam's words: "as quickly as possible, no changes" is rehost;
  "reduce database administration, no code change" is replatform; "use
  cloud-native features, scale" is refactor.
- **Discovery**: **AWS Application Discovery Service** (agentless through
  VMware vCenter, or agents for process and network detail) and **Migration
  Evaluator** (a business case from current usage), tracked in **AWS
  Migration Hub**. Build the **landing zone** first, with **Control
  Tower**.

## Move it

| What | Tool | How |
|---|---|---|
| servers (any OS, physical or virtual) | **AWS Application Migration Service (MGN)** | continuous **block-level** replication, test launches, then a short cutover |
| databases, same engine or not | **DMS** | **full load** then **CDC** (change data capture) to keep in sync until cutover: minimal downtime |
| schemas between different engines | **Schema Conversion Tool** / **DMS Schema Conversion** | converts schema and code (Oracle to PostgreSQL) |
| files and objects, online | **DataSync** | NFS, SMB, HDFS or object stores to S3, EFS or FSx; scheduled, incremental, verified |
| partners using SFTP, FTPS, AS2 | **Transfer Family** | managed endpoints writing to S3 or EFS |
| too much data for the network | **Snowball Edge** | shipped devices; rule of thumb: if the transfer would take more than a week over the link |
| on-premises apps during the transition | **Storage Gateway** | S3 File, FSx File, Volume and Tape gateways |

Transfer time is worth computing: 100 TB over a 1 Gbps link at full speed
is about 9 days (100 × 8,000 Gb ÷ 1 Gb/s ≈ 800,000 s), more in practice.

## Modernize

- **Containers** (ECS, EKS, Fargate), **serverless** (Lambda, Step
  Functions), **managed and purpose-built databases** (Aurora, DynamoDB).
- **Amazon MQ** for applications that already speak JMS, AMQP or MQTT: a
  managed ActiveMQ or RabbitMQ, without rewriting them for SQS.
- The **strangler fig** pattern: put a router in front of the old system
  and move features to new services one at a time, until the old system can
  be switched off.

| In a question | Answer |
|---|---|
| "migrate 500 servers quickly, minimal changes" | rehost with MGN |
| "Oracle to Aurora PostgreSQL, minimal downtime" | SCT / DMS Schema Conversion, then DMS full load + CDC |
| "copy 50 TB of NFS shares, then keep in sync until cutover" | DataSync |
| "2 PB, slow internet" | Snowball Edge |
| "existing app uses JMS, move with no code changes" | Amazon MQ |

## Traps

- **DMS** moves data; it does not convert schemas between engines (SCT
  does).
- **MGN** is for servers; **DMS** for databases; **DataSync** for files.
- Snowball for small amounts over a fast link is slower, not faster.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 4; AWS Prescriptive Guidance.

## Questions from open banks

- 3 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
