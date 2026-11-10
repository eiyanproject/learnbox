---
title: "Domain 2: Design for new solutions"
summary: 29% of the exam, the largest domain. Deployment strategy, business continuity, security controls, reliability, performance and cost for workloads designed from scratch.
order: 2
kind: quiz
---

**Weight: 29% of the scored questions.**

## Deployment and continuity

- Infrastructure as code (CloudFormation, CDK, StackSets), blue/green and
  canary releases, immutable infrastructure.
- Pick a DR strategy from the RTO/RPO and budget: backup and restore (hours),
  pilot light (tens of minutes), warm standby (minutes), multi-site
  active/active (near zero). **Aurora Global Database**, **DynamoDB global
  tables**, S3 Cross-Region Replication, AWS Backup cross-Region copies.

## Security by design

- Least privilege with roles, permissions boundaries and ABAC; secrets in
  **Secrets Manager** with rotation; encryption with KMS (multi-Region keys
  for replicated data); edge protection with **WAF**, **Shield Advanced**
  and **CloudFront**; private access with endpoints.

## Reliability and performance

- Loose coupling: SQS, SNS, EventBridge, Step Functions; idempotent
  consumers; backoff with jitter.
- Scale: Auto Scaling, serverless (Lambda, Fargate, DynamoDB on-demand),
  caching (CloudFront, ElastiCache, DAX), read replicas, purpose-built
  databases (Neptune for graphs, Timestream for time series, OpenSearch for
  search, Redshift for analytics).
- Data at scale: Kinesis Data Streams and Firehose, S3 data lakes with Glue
  and Athena, Lake Formation for permissions.

## Cost from day one

- Pricing models (On-Demand, Savings Plans, Spot), right storage classes,
  data transfer awareness (same-AZ, endpoints, CloudFront), managed services
  that remove idle capacity.

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 2; AWS service documentation.

## Questions from open banks

- 5 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
