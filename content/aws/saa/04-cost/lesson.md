---
title: "Domain 4: Design cost-optimized architectures"
summary: 20% of the exam. Paying for what you use - purchase options, storage tiers, right-sizing, serverless, data transfer, and the tools that show where the money goes.
order: 4
kind: quiz
---

**Weight: 20% of the scored questions.** Four tasks: cost-optimized storage,
compute, databases and networks.

## Paying for compute

| Option | For | Saving |
|---|---|---|
| On-Demand | short, unpredictable, can't be interrupted | none |
| **Savings Plans** | steady spend over 1 or 3 years; Compute SP follows you across families, Regions, Fargate and Lambda; EC2 Instance SP is cheaper but tied to a family in a Region | large |
| **Reserved Instances** | steady use of a known type; also for RDS, ElastiCache, Redshift, OpenSearch | large |
| **Spot** | interruptible: batch, CI, stateless workers | largest; two-minute warning |
| Dedicated Hosts | licensing per socket/core, compliance | costs more |

Right-size first (**Compute Optimizer** recommends), then commit. Stop
non-production instances out of hours. Use Graviton where software allows.
Serverless (**Lambda**, **Fargate**, **Aurora Serverless v2**, DynamoDB
on-demand) costs nothing - or little - when idle.

## Storage

- S3 classes from Standard down to Glacier Deep Archive; **Intelligent-
  Tiering** for unknown patterns; **lifecycle rules** to move and expire.
  Mind minimum storage durations and retrieval fees.
- **Requester Pays** buckets charge the downloader for requests and transfer.
- EBS: **gp3** is cheaper than gp2 with IOPS and throughput set separately;
  delete unattached volumes and old snapshots; the **snapshot archive** tier
  for long retention.
- EFS lifecycle to Infrequent Access and Archive; FSx options per workload.

## Data transfer

- Into AWS: free. Out to the internet: charged. Between AZs: charged both
  ways. Between Regions: charged.
- **Gateway endpoints** for S3 and DynamoDB are free and avoid NAT gateway
  processing charges; **NAT gateways** charge per hour and per GB.
- **CloudFront** reduces load and transfer from the origin, and transfer from
  AWS origins to CloudFront is free.
- One NAT gateway per AZ is more resilient; one shared NAT gateway is cheaper
  (and adds cross-AZ transfer). Pick by environment.
- **VPC peering** has no hourly charge; **Transit Gateway** charges per
  attachment and per GB, and simplifies many VPCs.

## Knowing what you spend

- **Cost allocation tags** (activated in Billing) break costs down by
  project or team; **Cost Explorer** charts and forecasts.
- **AWS Budgets** alerts on actual or forecast spend, and can act.
- **Cost and Usage Report / Data Exports** give line-item detail for Athena
  or QuickSight.
- **Organizations consolidated billing** pools volume discounts and Savings
  Plans across accounts.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 4; AWS pricing documentation.
