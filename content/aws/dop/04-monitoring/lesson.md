---
title: "Domain 4: Monitoring and logging"
summary: 15% of the exam. Collect, aggregate and store logs and metrics, audit and analyse them, and automate monitoring across accounts.
order: 4
kind: quiz
---

**Weight: 15% of the scored questions.**

## Collect and store

- **CloudWatch agent** (memory, disk, custom logs; config in Parameter
  Store), embedded metric format, custom metrics and high-resolution
  metrics, log groups with retention and KMS encryption.
- Centralize: **cross-account observability** (monitoring account linked to
  source accounts), subscription filters to Kinesis Data Firehose or a
  central account, organization CloudTrail, S3 lifecycle for archives.

## Analyse

- Metric filters and alarms, composite alarms, anomaly detection,
  **Logs Insights** queries, Contributor Insights, **X-Ray** and
  **CloudWatch Application Signals**, Container Insights and Lambda
  Insights, Athena over CloudTrail, ELB and VPC Flow Logs in S3.

## Automate

- Alarms to SNS, EventBridge and Systems Manager; dashboards defined as
  code; Config rules and conformance packs for configuration monitoring;
  Synthetics canaries for user journeys.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 4; AWS service documentation.
