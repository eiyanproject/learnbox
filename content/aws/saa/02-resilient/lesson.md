---
title: "Domain 2: Design resilient architectures"
summary: 26% of the exam. Loose coupling and scaling, then high availability, failover and disaster recovery - what keeps working when part of it does not.
order: 2
kind: quiz
---

A **resilient** architecture keeps working when part of it fails: an
instance dies, an Availability Zone loses power, traffic jumps tenfold, or
a whole Region has a bad day. This domain asks two things. Can the parts
absorb load without breaking each other (**loose coupling** and
**scaling**)? And does the system survive failures (**high availability**
and **disaster recovery**)? The method for reading questions is on the
Domain 1 page.

**Weight: 26% of the scored questions.** Two tasks: scalable, loosely
coupled architectures, and highly available or fault-tolerant ones.

## Loose coupling

*Practised in Serverless lessons 1-4.*

Two parts are **tightly coupled** when one calls the other and waits: if
the second is slow or down, the first fails too. **Loosely coupled** parts
hand work over and carry on; each can fail, scale or be replaced alone.

- **SQS** puts a **queue** between a producer and a consumer. A spike fills
  the queue instead of overwhelming the consumer, and a consumer that is
  down loses nothing. Key ideas:

  | | **Standard queue** | **FIFO queue** |
  |---|---|---|
  | Delivery | **at least once**: a message can arrive twice | **exactly-once** processing |
  | Order | best effort | strict, per **message group ID** |
  | Throughput | nearly unlimited | lower (higher with high-throughput mode) |

  A message being processed is hidden for the **visibility timeout**; if
  processing takes longer, it reappears and is processed **twice**, so set
  the timeout above the processing time. A **dead-letter queue** receives
  messages that failed `maxReceiveCount` times, so one bad message does not
  block the rest.
- **SNS** publishes one message to many subscribers. **Fan-out**: SNS in
  front of several SQS queues, so each consumer gets its own copy and its
  own pace.
- **EventBridge** routes events by **rules** that match their content: from
  AWS services, SaaS partners and your own applications, plus schedules.
- **Step Functions** runs multi-step workflows (a state machine) with
  retries, branches, waits, parallel steps and human approval, instead of
  functions calling each other.
- **API Gateway** fronts APIs, with throttling, authorization and caching;
  **Lambda** runs code per event; **ECS/EKS on Fargate** run containers
  without servers.
- **Stateless** tiers scale out: any instance can serve any request. Keep
  **session state** out of the instance, in **ElastiCache** or **DynamoDB**,
  not in memory or on local disk (sticky sessions are a workaround, not a
  fix).

| In a question | Answer |
|---|---|
| "orders must not be lost when the processing tier is down" | SQS between the tiers |
| "process in the order received, no duplicates" | SQS FIFO |
| "one event, several independent consumers" | SNS fan-out to SQS queues |
| "a message keeps failing and blocks processing" | a dead-letter queue |
| "messages are processed twice" | the visibility timeout is shorter than the processing time |
| "coordinate several steps with retries and approval" | Step Functions |

## High availability

*Practised in Compute lessons 2-3, Databases lessons 1-3, Containers lesson 4.*

An **Availability Zone** (AZ) is one or more data centres with their own
power and networking; a Region has three or more. **Highly available**
means surviving the loss of one AZ, so: at least **two AZs** for
everything.

- **Compute**: an **Application Load Balancer** in front of an **Auto
  Scaling group** spanning two or more AZs. The group replaces failed
  instances; with **ELB health checks**, it also replaces instances whose
  application fails while the machine still runs.
- **Relational databases**:

  | | **Multi-AZ** | **Read replica** |
  |---|---|---|
  | For | **availability** | **read scaling** |
  | Copy | synchronous standby in another AZ | asynchronous copy |
  | Serves reads? | no (except Multi-AZ DB clusters) | yes |
  | On failure | automatic failover, same endpoint, a minute or two | manual promotion |

  **Aurora** keeps six copies of the data across three AZs, with up to 15
  replicas that are also failover targets. **Aurora Global Database**
  replicates to other Regions, typically with under a second of lag.
  **DynamoDB global tables** are multi-Region and **multi-active** (writes in
  every Region).
- **RDS Proxy** pools database connections: it absorbs bursts of Lambda
  connections, and shortens failover for applications.
- **Shared files**: **EFS** is a Regional, multi-AZ file system for Linux
  (NFS); **FSx for Windows File Server** for SMB with Active Directory.
- **DNS**: **Route 53** failover (with health checks), latency, weighted,
  geolocation, geoproximity and multivalue policies.
- **S3** is already multi-AZ; **Cross-Region Replication** (versioning on
  both buckets) keeps a copy in another Region.
- **Service quotas** apply per Region: raise them in the standby Region
  before a disaster, not during it.

| In a question | Answer |
|---|---|
| "survive the failure of an AZ" | Multi-AZ: ALB + Auto Scaling across AZs, RDS Multi-AZ |
| "database read load is too high" | read replicas (or a cache), not Multi-AZ |
| "survive a Region failure" | cross-Region copies: Aurora Global Database, DynamoDB global tables, S3 CRR, Route 53 failover |
| "Lambda exhausts database connections" | RDS Proxy |
| "instances in two AZs must see the same files" | EFS |

## Disaster recovery

Two numbers define what "recovered" means:

- **RPO** (recovery point objective): how much **data** you can afford to
  lose, measured back in time from the failure. Backups every hour mean an
  RPO of up to an hour.
- **RTO** (recovery time objective): how long you can afford to be **down**.

Smaller numbers cost more. The four strategies, cheapest first:

| Strategy | Running in the DR Region before the disaster | RTO / RPO | Cost |
|---|---|---|---|
| **Backup and restore** | nothing but backups (snapshots, S3, AWS Backup copies) | hours / hours | lowest |
| **Pilot light** | data replicated and live; servers off or not created | tens of minutes | low |
| **Warm standby** | a scaled-down but complete, working copy | minutes | higher |
| **Multi-site active-active** | a full copy, serving traffic | near zero | highest |

The exam's words: "only the core (the database) running" is pilot light;
"a smaller full copy" is warm standby; "lowest RTO, both serving" is
multi-site. **AWS Elastic Disaster Recovery** (DRS) replicates servers
continuously at block level into AWS, for recovery in minutes.

## Traps

- **Multi-AZ is not a read replica**, and a read replica is not automatic
  failover.
- Multi-AZ protects against an AZ failure, **not a Region failure**: that
  needs cross-Region copies.
- "Highly available" does not need **multi-Region**; do not pay for more
  than asked.
- A single NAT gateway, bastion or instance in one AZ is a single point of
  failure.
- Do not choose a bigger instance when the question asks for availability:
  one large instance still fails.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 2; AWS whitepaper "Disaster Recovery of Workloads on AWS".

## Questions from open banks

- 60 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
