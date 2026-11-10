---
title: "Domain 3: Continuous improvement for existing solutions"
summary: 25% of the exam. Take a running workload and make it more operable, secure, performant, reliable and cheaper, usually under constraints like no downtime or minimal change.
order: 3
kind: quiz
---

**Weight: 25% of the scored questions.** The question describes something
already in production and a problem with it; look for the smallest change
that fixes the stated problem without breaking the other constraints.

## Operational excellence

- Observability: CloudWatch metrics, logs, alarms, Contributor Insights,
  X-Ray traces, Synthetics canaries.
- Automation: Systems Manager (Patch Manager, Automation runbooks,
  State Manager), EventBridge-driven remediation, Config rules with
  automatic remediation.
- Safe changes: CloudFormation change sets, drift detection, canaries and
  automatic rollback.

## Security improvements

- Remove long-lived keys (roles, IAM Roles Anywhere, Identity Center),
  rotate secrets, encrypt existing data (S3 Batch Operations, new encrypted
  RDS from an encrypted snapshot copy), GuardDuty, Inspector, Macie,
  Security Hub controls.

## Performance and reliability

- Fix the bottleneck the metrics show: caching (CloudFront, ElastiCache,
  DAX), read replicas and RDS Proxy, storage types (gp3/io2), placement,
  queues to absorb spikes, Multi-AZ and Auto Scaling health checks.

## Cost

- Right-size with **Compute Optimizer**, buy **Savings Plans** for steady
  baselines, use Spot for interruptible work, Graviton, storage lifecycle,
  delete idle resources (Trusted Advisor, Cost Optimization Hub), and cut
  data transfer (endpoints, same-AZ traffic, CloudFront).

Source: AWS Certified Solutions Architect - Professional (SAP-C02) exam
guide, Content Domain 3; AWS service documentation.
