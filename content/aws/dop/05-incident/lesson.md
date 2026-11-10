---
title: "Domain 5: Incident and event response"
summary: 14% of the exam. Manage event sources, act on events automatically, and troubleshoot failed deployments, scaling and services.
order: 5
kind: quiz
---

**Weight: 14% of the scored questions.**

## Event sources and routing

- **EventBridge** rules on AWS service events (EC2 state changes, Health,
  CodePipeline, GuardDuty, Config compliance changes), event buses across
  accounts, input transformers, archive and replay.
- **AWS Health** events (including organizational view) for scheduled
  maintenance and service issues; S3 event notifications; SNS fan-out.

## Automated response

- EventBridge → Lambda, Step Functions, SSM Automation runbooks, SNS;
  Config auto-remediation; Auto Scaling replacing unhealthy instances.
- **Systems Manager Incident Manager** response plans, escalation,
  runbooks; **OpsCenter** OpsItems.

## Troubleshooting

- Read the signal: CodeDeploy deployment logs and lifecycle event
  failures, CloudFormation stack events (the first failure), Auto Scaling
  activity history, ECS stopped-task reasons, Lambda throttles and DLQs,
  service quotas.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 5; AWS service documentation.
