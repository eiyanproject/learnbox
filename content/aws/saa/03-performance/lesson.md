---
title: "Domain 3: Design high-performing architectures"
summary: 24% of the exam. Choosing storage, compute, databases, networking and data pipelines that are fast enough and scale - and knowing which knob each one has.
order: 3
kind: quiz
---

**Weight: 24% of the scored questions.** Five tasks: storage, compute,
databases, networks, and data ingestion and transformation.

## Storage

| Need | Choose |
|---|---|
| Block storage for one instance | **EBS**: gp3 (general, IOPS and throughput set independently), io2 / io2 Block Express (highest IOPS, lowest latency), st1 (throughput HDD), sc1 (cold HDD) |
| Fastest scratch space, lost on stop | **instance store** |
| Shared file system, Linux | **EFS** |
| HPC file system linked to S3 | **FSx for Lustre** |
| SMB / Windows | **FSx for Windows File Server**; ONTAP and OpenZFS for those ecosystems |
| Objects at any scale | **S3**; multipart upload for big objects, Transfer Acceleration for distant clients |

## Compute

- Instance families: **C** compute optimized, **M** general purpose,
  **R/X** memory optimized, **I/D** storage optimized, **P/G/Inf/Trn**
  accelerated. Graviton (`g` suffix) for better price-performance.
- **Auto Scaling**: target tracking (keep a metric at a value), step,
  scheduled (known peaks), predictive.
- **Placement groups**: cluster (low latency, one AZ), spread (separate
  hardware), partition (large distributed systems).
- **Lambda**: memory sets CPU too - more memory, more CPU.
- **Batch** for batch jobs; **EMR** for Spark/Hadoop.

## Databases

- **DynamoDB**: key-value/document, single-digit milliseconds at any scale;
  on-demand or provisioned capacity; **DAX** for microsecond reads.
- **Aurora**: MySQL/PostgreSQL compatible, up to 15 low-latency replicas,
  storage grows by itself; Aurora Serverless v2 scales capacity.
- **RDS** engines; read replicas for read scaling; Provisioned IOPS storage.
- **ElastiCache** (Redis OSS, Valkey, Memcached) caches query results and
  sessions.
- Purpose-built: **Neptune** (graph), **Timestream** (time series),
  **OpenSearch** (search), **Redshift** (warehouse), **DocumentDB**
  (MongoDB-compatible).

## Networking

- **CloudFront** caches content at edge locations, for static and dynamic
  content. **Global Accelerator** gives two static anycast IPs and routes TCP
  and UDP over the AWS backbone to the nearest healthy endpoint - for
  non-HTTP traffic and fast regional failover.
- Load balancers: **ALB** (HTTP, layer 7, path and host routing), **NLB**
  (TCP/UDP, layer 4, static IPs, extreme throughput), **GWLB** (appliances).
- Hybrid: VPN, Direct Connect, **PrivateLink** (private access to a service
  in another VPC).

## Data ingestion and analytics

- **Kinesis Data Streams**: real-time streams, many consumers, replay.
  **Amazon Data Firehose**: delivers streams to S3, Redshift, OpenSearch with
  no code. **Managed Service for Apache Flink**: stream processing.
- **Glue**: serverless ETL and the Data Catalog. **Athena**: SQL on S3,
  cheaper and faster on columnar formats (Parquet, ORC) and partitions.
  **Lake Formation**: permissions for a data lake.
- Moving data in: **DataSync** (online transfers and sync), **Storage
  Gateway** (on-premises access to cloud storage), **Snowball Edge**
  (offline, terabytes to petabytes), **Transfer Family** (SFTP/FTPS to S3 or
  EFS).

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 3; AWS service documentation.

## Questions from open banks

- 55 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
