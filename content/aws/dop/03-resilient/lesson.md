---
title: "Domain 3: Resilient cloud solutions"
summary: 15% of the exam. High availability across AZs and Regions, scaling that keeps up with demand, and automated recovery to meet RTO and RPO.
order: 3
kind: quiz
---

**Weight: 15% of the scored questions.**

## Highly available

- Spread across AZs: Auto Scaling groups with ELB health checks, Multi-AZ
  RDS and Aurora, EFS, DynamoDB; remove single points of failure (one NAT
  gateway, one instance).
- Multi-Region: Route 53 health checks and failover, Aurora Global
  Database, DynamoDB global tables, S3 replication, ECR replication.

## Scalable

- Auto Scaling policies (target tracking, step, predictive, scheduled),
  warm pools and lifecycle hooks, ECS service auto scaling, Lambda
  concurrency (reserved and provisioned), DynamoDB on-demand or auto scaling,
  caching and read replicas, loose coupling with queues.

## Automated recovery

- Backups with **AWS Backup** plans (cross-Region and cross-account copies,
  vault lock), point-in-time recovery, restore testing.
- Automated failover runbooks (Systems Manager Automation, Step Functions),
  **Application Recovery Controller**, **Elastic Disaster Recovery**,
  chaos experiments with **AWS Fault Injection Service** to prove it works.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 3; AWS service documentation.
