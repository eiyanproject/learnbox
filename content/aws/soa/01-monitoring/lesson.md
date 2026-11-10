---
title: "Domain 1: Monitoring, logging, analysis, remediation and performance"
summary: 22% of the exam. Collecting the right metrics and logs, alarms that mean something, automatic remediation with EventBridge and Systems Manager, and tuning compute, storage and databases.
order: 1
kind: quiz
---

**Weight: 22% of the scored questions.**

- **CloudWatch agent**: memory, disk and process metrics and log files from
  EC2 and on-premises servers (the hypervisor cannot see inside the guest).
  **Container Insights** for ECS and EKS.
- **Alarms**: thresholds over evaluation periods; actions to SNS, Auto
  Scaling, EC2 (stop, terminate, reboot, **recover**), Systems Manager.
  **Composite alarms** combine alarms with AND/OR to cut noise.
- **Dashboards** can show metrics from several accounts and Regions.
- **Logs**: retention, metric filters, **subscription filters** that stream to
  Lambda, Firehose or OpenSearch, Logs Insights for queries.
- **EventBridge** routes events (including CloudTrail API calls, Config
  changes, GuardDuty findings, scheduled rules) to targets. A Lambda target
  needs a resource-based permission for `events.amazonaws.com`.
- **Systems Manager**: **Automation runbooks** (AWS-provided and your own),
  **Run Command**, **Patch Manager** with maintenance windows.
- Performance: **gp3** (IOPS and throughput independent of size) over gp2
  burst credits; **RDS Performance Insights** for the top SQL and waits;
  **RDS Proxy** for connection storms; **EFS** throughput modes and lifecycle;
  **placement groups**; S3 multipart upload and Transfer Acceleration.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 1; AWS service documentation.
