---
title: "Domain 4: Design cost-optimized architectures"
summary: 20% of the exam. Paying for what you use - purchase options, storage tiers, right-sizing, serverless, data transfer, and the tools that show where the money goes.
order: 4
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **cost-optimized** | meeting every requirement for the least money |
| **On-Demand** | pay per second, no commitment |
| **Savings Plans** | a committed spend per hour for 1 or 3 years; Compute Savings Plans span families, Regions, Fargate and Lambda |
| **Reserved Instances** | a commitment to a known instance type; also for RDS and others |
| **Spot** | spare capacity up to 90% off, with a two-minute warning |
| **checkpoint** | saving progress so interrupted work can resume |
| **Dedicated Hosts** | whole physical servers, for per-socket licences or compliance |
| **right-size** | match instance size to actual use |
| **Compute Optimizer** | recommends instance sizes from actual use |
| **Instance Scheduler** | stops instances outside working hours |
| **serverless** | costs little or nothing when idle |
| **storage classes**, **Intelligent-Tiering**, **lifecycle rules** | S3's cost tools |
| **minimum storage duration**, **retrieval fee** | why cold classes cost more for data read often |
| **Requester Pays** | the downloader pays for requests and transfer |
| **Elastic Volumes** | change an EBS volume's type or size with no downtime |
| **unattached volume** | an EBS disk on no instance, still billed |
| **snapshot archive** | a cheaper tier for long-kept EBS snapshots |
| **incomplete multipart upload** | parts of a failed upload, billed until removed |
| **data transfer** | charged out to the internet, between AZs (each way) and between Regions |
| **gateway endpoint** | free, and keeps S3 and DynamoDB traffic off the NAT gateway |
| **Transit Gateway** | charged per attachment and per GB |
| **cost allocation tags** | break the bill down by project or team |
| **Cost Explorer** | charts and forecasts spend |
| **AWS Budgets** | alerts on actual or forecast spend, and can take actions |
| **Cost and Usage Report / Data Exports** | line-item billing detail |
| **QuickSight** | AWS's dashboard service |
| **Cost Anomaly Detection**, **Cost Optimization Hub**, **Trusted Advisor** | flag unusual spend / list savings |
| **consolidated billing** | usage added up across an organization's accounts |

---

**Cost-optimized** means meeting **every** requirement for the least money,
not simply the cheapest option. An answer that saves money but loses data,
or breaks availability the question asked for, is wrong. Most savings come
from four habits: pay only for what runs, commit to what always runs, store
data in the class that matches how it is used, and avoid paying to move
data. The method for reading questions is on the Domain 1 page.

**Weight: 20% of the scored questions.** Four tasks: cost-optimized
storage, compute, databases and networks.

## Paying for compute

The same instance can be bought in several ways:

| Option | For | Saving |
|---|---|---|
| **On-Demand** | short, unpredictable work that must not be interrupted | none |
| **Savings Plans** | a steady **spend per hour**, committed for 1 or 3 years. **Compute Savings Plans** apply across instance families, Regions, **Fargate** and **Lambda**; **EC2 Instance Savings Plans** save more but are tied to one family in one Region | up to about 66% / 72% |
| **Reserved Instances** | steady use of a known instance type; also for **RDS**, ElastiCache, Redshift, OpenSearch | up to about 72% |
| **Spot** | interruptible work: batch, CI, stateless workers, anything that checkpoints | up to 90%, with a **two-minute** warning before AWS takes it back |
| **Dedicated Hosts** | software licensed per socket or core, compliance | costs more |

The order of work: **right-size first** (**Compute Optimizer** recommends
smaller or different instances from actual use), then commit for what is
left. Also: stop non-production instances outside working hours (Instance
Scheduler), and use **Graviton** where the software allows. **Serverless**
(Lambda, Fargate, Aurora Serverless v2, DynamoDB on-demand) costs nothing,
or little, when idle, which suits spiky or occasional workloads.

| In a question | Answer |
|---|---|
| "steady 24/7, for three years" | Savings Plans or Reserved Instances |
| "mix of EC2, Fargate and Lambda, flexibility" | Compute Savings Plan |
| "batch job that can restart, cheapest" | Spot |
| "must not be interrupted" | never Spot |
| "instances are mostly idle" | right-size (Compute Optimizer), or move to serverless |

## Storage

*Practised in Foundations lesson 5, Containers lesson 1.*

- **S3 storage classes** from **Standard** down to **Glacier Deep Archive**:
  the colder the class, the cheaper to store and the more expensive (and
  slower) to read. **Intelligent-Tiering** moves objects by itself when
  access patterns are unknown or change. **Lifecycle rules** move objects to
  colder classes and **expire** them. ❗ Colder classes have **minimum
  storage durations** (30 days for the IA classes, 90 for Glacier Instant
  and Flexible, 180 for Deep Archive) and **retrieval fees**: moving data
  that is read often to them costs more, not less.
- **Requester Pays** buckets charge the downloader for requests and
  transfer.
- **EBS**: **gp3** is cheaper than gp2, with IOPS and throughput set
  separately (change with Elastic Volumes, no downtime); delete
  **unattached volumes** and old **snapshots**; the **snapshot archive**
  tier for long retention.
- **EFS** lifecycle management moves files to Infrequent Access and Archive;
  **FSx** has options per workload.
- Lifecycle rules for **ECR images** and S3 **noncurrent versions** and
  **incomplete multipart uploads** remove storage nobody uses.

| In a question | Answer |
|---|---|
| "access pattern unknown" | S3 Intelligent-Tiering |
| "rarely read after 30 days, kept 7 years" | lifecycle: Standard-IA, then Glacier Deep Archive, then expire |
| "archive, retrieval within 12 hours is fine" | Glacier Flexible Retrieval (or Deep Archive for 48 hours) |
| "lower EBS cost with no downtime" | gp2 to gp3 |

## Data transfer

Data transfer is the cost people forget:

| Traffic | Charged? |
|---|---|
| into AWS from the internet | free |
| out to the internet | yes, per GB |
| between AZs in a Region | yes, in **each** direction |
| between Regions | yes |
| from AWS origins to CloudFront | free |

- **Gateway endpoints** for S3 and DynamoDB are free, and keep that
  traffic off the **NAT gateway**, which charges per hour **and per GB
  processed** (Networking lesson 3).
- **CloudFront** serves cached copies, reducing origin load and transfer.
- One **NAT gateway per AZ** is resilient; one shared NAT gateway is
  cheaper but adds cross-AZ charges and a single point of failure. Choose
  by environment: production versus development.
- **VPC peering** has no hourly charge; **Transit Gateway** charges per
  attachment and per GB, and pays off when many VPCs connect.

| In a question | Answer |
|---|---|
| "high NAT gateway charges from S3 traffic" | an S3 gateway endpoint |
| "reduce transfer cost for global downloads" | CloudFront |

## Knowing what you spend

- **Cost allocation tags** (activated in the Billing console) break costs
  down by project or team. **Cost Explorer** charts and forecasts spend.
- **AWS Budgets** alerts on actual or **forecast** spend, and can take
  actions (apply a policy, stop instances).
- **Cost and Usage Report / Data Exports** give line-item detail, to query
  with Athena or chart in QuickSight.
- **Cost Anomaly Detection** flags unusual spend; **Cost Optimization Hub**
  and **Trusted Advisor** list savings.
- **Organizations consolidated billing** adds up usage across accounts for
  volume discounts, and shares Savings Plans and Reserved Instances.

## Traps

- The cheapest option must still meet **every** requirement.
- **Spot** for anything that "must not be interrupted" is wrong.
- **Glacier** classes for data read often cost more (retrieval fees,
  minimum durations).
- **Multi-Region** or **Shield Advanced** when the question did not ask for
  them is paying for nothing.
- Traffic **between AZs is not free**.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 4; AWS pricing documentation.

## Questions from open banks

- 49 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
