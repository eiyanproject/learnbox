---
title: "Domain 2: Reliability and business continuity"
summary: 22% of the exam. Scaling and caching, health checks and Multi-AZ that actually fail over, and backups and restores that meet the RPO and RTO.
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
| **reliability** | still serving when parts fail or load grows |
| **business continuity** | getting the system and data back after something bigger |
| **warm pool** | pre-initialized instances kept ready for fast scale-out |
| **lifecycle hook** | pauses an instance while launching or terminating, to run setup or copy logs |
| **instance refresh** | replaces instances gradually with a new launch template version |
| **replica auto scaling** | Aurora adding and removing replicas with load |
| **cluster mode** | ElastiCache spreading writes across shards |
| **origin failover** | CloudFront switching from a primary to a secondary origin |
| **ELB target health check** | decides where the load balancer sends traffic |
| **ELB health check type** | makes Auto Scaling replace instances whose application fails |
| **EC2 status checks** | the default Auto Scaling health check: only whether the instance runs |
| **Route 53 health checkers** | on the internet; the security group must allow them |
| **DNS endpoint** | RDS's name, moved to the standby on failover; never cache its IP |
| **AWS Backup** | backup plans, vaults, recovery points, cross-Region and cross-account copies |
| **backup plan** | schedule, retention and cold-storage lifecycle, assigned by tag |
| **vault** / **recovery point** | holds backups / one backup |
| **Vault Lock** | makes backups immutable, even for root |
| **Data Lifecycle Manager** | automates EBS snapshots and AMIs by tag |
| **point-in-time restore** | always to a new instance or table, with a new endpoint |
| **delete marker** | hides a "deleted" versioned object; delete it to restore |
| **RTO**, **RPO** | how long you can be down / how much data you can lose |
| **backup and restore**, **pilot light**, **warm standby**, **multi-site active/active** | the DR strategies |

---

**Reliability** is the system still serving when parts fail or load
grows; **business continuity** is getting it and its data back after
something bigger goes wrong. Operational questions here are practical: why
didn't the failover work, why are restored backups missing data, why did
scaling react too late?

**Weight: 22% of the scored questions.**

## Scaling and caching

*Practised in Compute lesson 3, Containers lesson 2.*

- **Auto Scaling**: target tracking, step and scheduled policies (Compute
  lesson 3); **warm pools** keep pre-initialized instances stopped or
  running, ready for a fast scale-out when instances take long to boot;
  **lifecycle hooks** pause an instance while launching or terminating, to
  run setup or copy logs off first; **instance refresh** replaces instances
  gradually with a new launch template version.
- **Database scaling**: Aurora **replica auto scaling**, DynamoDB **auto
  scaling** or **on-demand** capacity, ElastiCache **cluster mode** for
  spreading writes across shards.
- **Caching**: **CloudFront** (with **origin failover** groups: a primary
  and a secondary origin), and **ElastiCache** in front of databases.

## Health checks that work

*Practised in Compute lesson 2, Containers lesson 4.*

- **ELB target health checks** decide where the load balancer sends
  traffic: a path, success codes, interval and thresholds. An Auto Scaling
  group uses **EC2 status checks** by default; with the **ELB health check
  type** on, it also **replaces** instances whose application fails.
- **Route 53 health checks** drive DNS failover. ❗ The checkers are on the
  internet: the endpoint's **security group** must allow their IP ranges,
  or every check fails.
- **RDS Multi-AZ** failover keeps the **DNS endpoint** and points it at the
  standby. Applications must **reconnect** and must **not cache the IP
  address**; a client that resolved the name once and kept the IP stays
  broken.

## Backups and restores

*Practised in Foundations lesson 5, Databases lessons 1-2.*

- **AWS Backup**: **backup plans** (schedule, retention, lifecycle to cold
  storage) assigned to resources by tag; **vaults** that hold recovery
  points; **Vault Lock** makes them immutable, even for the root user;
  **cross-Region** and **cross-account** copies.
- **Data Lifecycle Manager** automates EBS snapshots and AMIs by tag.
- **Point-in-time restore**: RDS restores to any second within the
  retention period, always to a **new** instance (with a new endpoint, so
  applications must be repointed); DynamoDB PITR restores to a new table.
- **S3 versioning**: a "deleted" object only has a **delete marker** on top;
  restore it by deleting the marker, or by copying an old version back.
- **FSx** backups for its file systems.

## Disaster recovery

The four strategies (Solutions Architect Domain 2 page) trade cost for RTO
and RPO: **backup and restore** (hours), **pilot light** (data live,
servers off), **warm standby** (a small full copy running), **multi-site
active/active** (near zero). The operational point: a DR plan works only if
it is **tested**, and the quotas, AMIs and secrets the standby needs exist
in its Region.

| In a question | Answer |
|---|---|
| "instances take 10 minutes to boot, scale-out is too slow" | a warm pool (or scheduled scaling ahead of the peak) |
| "copy logs before an instance is terminated" | a termination lifecycle hook |
| "Auto Scaling keeps instances whose app has crashed" | the ELB health check type |
| "Route 53 health checks always fail" | the security group blocks the health checkers |
| "backups must not be deletable, even by admins" | AWS Backup Vault Lock |
| "restore the database to 10:42 yesterday" | point-in-time restore to a new instance |
| "recover an object someone deleted" | delete the delete marker (versioning) |

## Traps

- A restore creates a **new** RDS instance with a **new endpoint**.
- Multi-AZ does not help if the application caches the database's IP.
- An Auto Scaling group with EC2 health checks does not notice a crashed
  application.
- Snapshots in the same Region do not protect against a Regional problem:
  copy them.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 2; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
