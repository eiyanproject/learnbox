---
title: "Domain 2: Reliability and business continuity"
summary: 22% of the exam. Scaling and caching, health checks and Multi-AZ that actually fail over, and backups and restores that meet the RPO and RTO.
order: 2
kind: quiz
---

**Weight: 22% of the scored questions.**

- **Scaling**: Auto Scaling policies, **warm pools** (pre-initialized
  instances for faster scale-out), **lifecycle hooks** (run actions when
  instances launch or terminate), instance refresh. Database scaling: Aurora
  replica auto scaling, DynamoDB auto scaling or on-demand, ElastiCache
  cluster mode for write scaling.
- **Health checks**: ELB target health (path, success codes, thresholds) and
  Auto Scaling's ELB health checks; **Route 53 health checks** for DNS
  failover - and security groups must let the health checkers in.
- **Multi-AZ**: an RDS failover changes which instance the DNS endpoint
  points to; applications must reconnect (and not cache IPs).
- **Backups**: **AWS Backup** plans and vaults (**Vault Lock** makes
  recovery points immutable), cross-Region and cross-account copies;
  **Data Lifecycle Manager** for EBS snapshots and AMIs; **point-in-time
  restore** for RDS (to a **new** instance) and DynamoDB.
- **Versioning** in S3 (restore by deleting a delete marker or copying an old
  version back) and FSx backups.
- **Caching**: CloudFront (and origin failover groups), ElastiCache.
- **DR strategies**: backup and restore, pilot light, warm standby,
  multi-site active/active.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 2; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
