---
title: "Domain 4: Accelerate workload migration and modernization"
summary: 20% of the exam. Assess a portfolio, pick a migration strategy per workload, move data and servers with the right tools, and modernize once in AWS.
order: 4
kind: quiz
---

**Weight: 20% of the scored questions.**

## Assess and plan

- **The 7 Rs**: retire, retain, rehost (lift and shift), relocate (for
  example VMware Cloud on AWS), repurchase (move to SaaS), replatform (lift,
  tinker and shift, for example to RDS), refactor (re-architect).
- Discovery with **AWS Application Discovery Service** (agentless or agent)
  or **Migration Evaluator**, tracked in **AWS Migration Hub**; landing zone
  first with **Control Tower**.

## Move it

- Servers: **AWS Application Migration Service (MGN)** for continuous
  block-level replication and cutover.
- Databases: **DMS** (full load plus CDC for minimal downtime) and
  **Schema Conversion Tool** / DMS Schema Conversion for heterogeneous
  engines.
- Files and objects: **DataSync** (NFS/SMB/HDFS/object to S3, EFS, FSx,
  scheduled and verified), **Transfer Family** (SFTP/FTPS/AS2 endpoints),
  **Snowball Edge** when the network is too slow (rule of thumb: if the
  transfer takes more than a week over the link).
- Hybrid storage during transition: **Storage Gateway** (S3 File, FSx File,
  Volume, Tape).

## Modernize

- Containers (ECS, EKS, Fargate), serverless (Lambda, Step Functions),
  managed and purpose-built databases (Aurora, DynamoDB), managed messaging
  (Amazon MQ for existing JMS/AMQP clients), decomposition with the
  strangler fig pattern.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 4; AWS Prescriptive Guidance.
