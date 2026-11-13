---
title: "Domain 2: Design for new solutions"
summary: 29% of the exam, the largest domain. Deployment strategy, business continuity, security controls, reliability, performance and cost for workloads designed from scratch.
order: 2
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **design pillars** | deployment, continuity, security, reliability, performance, cost |
| **infrastructure as code** | CloudFormation, CDK, StackSets: reproducible environments |
| **immutable infrastructure** | replace, never patch in place |
| **blue/green**, **canary** | switch between two versions / a small share first |
| **RTO** / **RPO** | allowed downtime / allowed data loss |
| **backup and restore**, **pilot light**, **warm standby**, **multi-site active/active** | DR strategies, cheapest first |
| **Aurora Global Database** | up to five secondary Regions, under a second behind; one writer Region |
| **DynamoDB global tables** | writes accepted in every Region |
| **permissions boundary** | caps what delegated administrators can grant |
| **ABAC** | attribute-based access control: policies comparing tags |
| **multi-Region KMS keys** | the same key in several Regions for replicated data |
| **Shield Advanced** | paid DDoS response and cost protection |
| **loose coupling** | SQS, SNS, EventBridge, Step Functions between parts |
| **idempotent** | safe to process twice |
| **exponential backoff and jitter** | growing, randomized retry waits, so clients do not retry in lockstep |
| **purpose-built databases** | Neptune, Timestream, OpenSearch, Redshift |
| **data lake** | raw data in S3, catalogued by Glue and queried by Athena |
| **Lake Formation** | table- and column-level permissions on the lake |
| **pricing model** | On-Demand, Savings Plans or Spot per part of the workload |
| **chatty components** | parts that exchange a lot of data; keep them in the same AZ |

---

Here the workload does not exist yet: you design it. Questions give the
business requirements (users, data volume, availability, recovery targets,
budget, compliance) and ask for the architecture that meets them all.
Every AWS design pillar shows up: deployment, continuity, security,
reliability, performance, cost. The method for reading questions is on the
Domain 1 page.

**Weight: 29% of the scored questions**, the largest domain.

## Deployment and continuity

*Practised in Operations lesson 3, CI/CD lessons 1-2.*

- **Infrastructure as code** (CloudFormation, CDK, StackSets for many
  accounts) so every environment is reproducible; **immutable
  infrastructure** (replace, never patch in place); **blue/green** and
  **canary** releases with automatic rollback.
- Choose the **DR strategy** from the **RTO** (allowed downtime), **RPO**
  (allowed data loss) and the budget:

  | Strategy | RTO | Building blocks |
  |---|---|---|
  | Backup and restore | hours | AWS Backup cross-Region copies, snapshots, IaC to rebuild |
  | Pilot light | tens of minutes | replicated data (Aurora Global Database, S3 CRR), servers off |
  | Warm standby | minutes | a scaled-down full copy, Route 53 failover |
  | Multi-site active/active | near zero | **DynamoDB global tables** or Aurora Global Database, latency routing |

  **Aurora Global Database** replicates to up to five secondary Regions,
  usually under a second behind, and a secondary can be promoted in about a
  minute. **DynamoDB global tables** accept writes in every Region.

## Security by design

*Practised in Foundations lessons 3-6, Security lessons 1-2.*

- **Least privilege** with roles, **permissions boundaries** for delegated
  administration, and **ABAC** (attribute-based access control: policies
  that compare tags, such as "a principal tagged `project=x` may use
  resources tagged `project=x`", so new projects need no new policies).
- **Secrets Manager** with rotation; **KMS** for encryption, with
  **multi-Region keys** for data replicated between Regions.
- **Edge protection**: **CloudFront** in front, **WAF** rules, **Shield
  Advanced** for DDoS response and cost protection.
- **Private access**: VPC endpoints, private subnets, no public databases.

## Reliability and performance

*Practised in Serverless lessons 1-4, Databases lessons 1-3.*

- **Loose coupling**: SQS, SNS, EventBridge, Step Functions; **idempotent**
  consumers (safe to process twice); retries with **exponential backoff and
  jitter**, so clients do not retry in lockstep.
- **Scale**: Auto Scaling; serverless (Lambda, Fargate, DynamoDB
  on-demand); **caching** at each layer (CloudFront, ElastiCache, DAX); read
  replicas; **purpose-built databases** (Neptune for graphs, Timestream for
  time series, OpenSearch for search, Redshift for analytics).
- **Data at scale**: Kinesis Data Streams and Firehose for ingestion; an S3
  **data lake** catalogued by Glue and queried by Athena; **Lake Formation**
  for table- and column-level permissions on it.

## Cost from day one

- The right **pricing model** per workload part (On-Demand, Savings Plans,
  Spot); the right **storage classes** with lifecycle rules; awareness of
  **data transfer** (keep chatty components in the same AZ, gateway
  endpoints, CloudFront); **managed and serverless** services that remove
  idle capacity.

| In a question | Answer |
|---|---|
| "RPO of seconds, RTO under a minute, global relational database" | Aurora Global Database |
| "users in several Regions write locally, key-value" | DynamoDB global tables |
| "encrypted data replicated across Regions, one key ID" | KMS multi-Region keys |
| "permissions must scale to hundreds of projects" | ABAC with tags |
| "retries overwhelm the service after an outage" | exponential backoff with jitter |

## Traps

- Choose the **cheapest** strategy that meets the RTO and RPO, not the
  best one.
- **Aurora Global Database** has one writer Region; for writes in several
  Regions, DynamoDB global tables.
- A design that meets everything but needs skills the story says the team
  lacks is usually wrong.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 2; AWS service documentation.

## Questions from open banks

- 5 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
