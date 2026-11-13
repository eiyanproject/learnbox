---
title: "Domain 3: Design high-performing architectures"
summary: 24% of the exam. Choosing storage, compute, databases, networking and data pipelines that are fast enough and scale - and knowing which knob each one has.
order: 3
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **high-performing** | fast enough, and still fast as load grows |
| **block storage** | a disk for one instance: EBS |
| **gp3**, **io2 / io2 Block Express** | general-purpose SSD / high, consistent IOPS |
| **IOPS**, **throughput** | operations per second / data per second |
| **instance store** | fast local disk, lost when the instance stops |
| **EFS**, **FSx for Lustre**, **FSx for Windows**, **FSx for NetApp ONTAP**, **OpenZFS** | shared file systems for different needs |
| **HPC** | high-performance computing |
| **multipart upload** | uploading a big object in parts, in parallel |
| **Transfer Acceleration** | faster S3 uploads from far away, through edge locations |
| **prefix** (S3 scaling) | about 3,500 writes and 5,500 reads per second each |
| **instance families** | M general, C compute, R/X memory, I/D storage, P/G/Inf/Trn accelerators |
| **burstable** | T types, which use CPU credits |
| **Graviton** | AWS's Arm processor (`g` in the name) |
| **target tracking**, **step**, **scheduled**, **predictive** | Auto Scaling policy types |
| **warm pool** | instances kept ready for fast scale-out |
| **placement group** | cluster (close, one AZ), spread (separate hardware), partition (separate racks) |
| **Lambda memory** | also sets CPU; 15-minute limit; provisioned concurrency removes cold starts |
| **AWS Batch**, **EMR** | batch jobs / Spark and Hadoop |
| **DAX** | microsecond DynamoDB reads |
| **Aurora Serverless v2** | Aurora capacity that scales with load |
| **Provisioned IOPS** | RDS storage with consistent I/O |
| **purpose-built databases** | Neptune (graph), Timestream (time series), OpenSearch (search), Redshift (warehouse), DocumentDB (MongoDB), Keyspaces (Cassandra) |
| **data warehouse** | a database for analytics over large data |
| **CloudFront** / **Global Accelerator** | caches at the edge / two static anycast IPs, any TCP or UDP, no caching |
| **ALB**, **NLB**, **GWLB** | layer 7 / layer 4 / layer 3 load balancers |
| **PrivateLink** | private access to a service in another VPC |
| **Kinesis Data Streams** | real-time streams with many consumers and replay |
| **Amazon Data Firehose** | delivers a stream to S3, Redshift or OpenSearch with no code |
| **Managed Service for Apache Flink** | processes streams |
| **Glue** / **Data Catalog** | serverless ETL / table definitions |
| **ETL** | extract, transform, load |
| **Athena** | SQL on S3; faster on columnar formats with partitions |
| **columnar format** | Parquet, ORC: data stored by column, so queries read less |
| **partition** (data) | a folder of data by key, such as date, so queries skip the rest |
| **Lake Formation** | manages data lake permissions |
| **DataSync**, **Storage Gateway**, **Snowball Edge**, **Transfer Family** | online copies / on-premises apps using cloud storage / shipped device / SFTP and FTP endpoints |
| **sharding** | splitting data across several databases |

---

**High-performing** means fast enough, and still fast as load grows. Most
questions in this domain describe a workload (lots of small reads, huge
sequential files, users on several continents, a stream of events) and ask
which service, or which setting, fits it. The key is knowing what each
service is good at, and which knob it has. The method for reading questions
is on the Domain 1 page.

**Weight: 24% of the scored questions.** Five tasks: storage, compute,
databases, networks, and data ingestion and transformation.

## Storage

*Practised in Foundations lesson 5.*

First decide the **kind** of storage, then the option:

| Need | Choose |
|---|---|
| a disk for one instance (block) | **EBS**: **gp3** general purpose, with IOPS and throughput set apart from size; **io2 / io2 Block Express** for the highest IOPS and lowest latency (critical databases); **st1** throughput HDD for large sequential reads; **sc1** cold HDD, cheapest |
| the fastest scratch space, lost when the instance stops | **instance store** |
| a file system shared by many Linux instances | **EFS** (NFS) |
| a file system for HPC and machine learning, linked to S3 | **FSx for Lustre** |
| Windows file shares (SMB, Active Directory) | **FSx for Windows File Server**; **FSx for NetApp ONTAP** and **OpenZFS** for those ecosystems |
| objects at any scale | **S3**: **multipart upload** for big objects, **Transfer Acceleration** for distant clients |

EBS volumes live in **one AZ** and usually attach to one instance; EFS is
Regional and shared. S3 scales by **prefix**: about 3,500 writes and 5,500
reads per second per prefix, so spread hot keys over several prefixes.

## Compute

*Practised in Compute lessons 1-3, Serverless lesson 3.*

- **Instance families** by their letter:

  | Letter | Optimized for |
  |---|---|
  | **M** (and T, burstable) | general purpose |
  | **C** | compute |
  | **R**, **X** | memory |
  | **I**, **D** | storage (fast local disks) |
  | **P**, **G**, **Inf**, **Trn** | accelerators (GPUs, inference, training) |

  A `g` after the number (`m7g`) means **Graviton**, AWS's Arm processor:
  better price-performance where the software supports Arm.
- **Auto Scaling** policies: **target tracking** keeps a metric at a value
  (the default answer for "scale with load"); **step** reacts by alarm
  size; **scheduled** for known peaks ("every weekday at 8:00"); **predictive**
  learns daily or weekly patterns. Instances that take long to boot can
  wait ready in a **warm pool**.
- **Placement groups**:

  | Type | Places instances | For |
  |---|---|---|
  | **Cluster** | close together, in one AZ | lowest latency, highest throughput between nodes (HPC) |
  | **Spread** | on separate hardware | a few critical instances that must not fail together |
  | **Partition** | in groups on separate racks | large distributed systems (Hadoop, Kafka, Cassandra) |

- **Lambda**: CPU grows with the **memory** setting, so a slow function may
  need more memory; at most **15 minutes** per invocation; **provisioned
  concurrency** removes cold starts.
- **AWS Batch** for batch jobs; **EMR** for Spark and Hadoop.

## Databases

*Practised in Databases lessons 1-3.*

- **DynamoDB**: key-value and document, single-digit millisecond responses
  at any scale; **on-demand** or **provisioned** capacity; **DAX** caches
  reads for **microsecond** responses.
- **Aurora**: MySQL- and PostgreSQL-compatible, up to **15** low-latency
  replicas, storage that grows by itself; **Aurora Serverless v2** scales
  capacity with load.
- **RDS** for the standard engines; **read replicas** scale reads;
  **Provisioned IOPS** storage for consistent I/O.
- **ElastiCache** (Redis OSS, Valkey, Memcached) caches query results and
  sessions in memory, in front of a database.
- **Purpose-built** databases:

  | Data | Service |
  |---|---|
  | relationships (social graphs, fraud rings) | **Neptune** (graph) |
  | measurements over time (sensors, metrics) | **Timestream** |
  | full-text and log search | **OpenSearch Service** |
  | analytics over large data (data warehouse) | **Redshift** |
  | MongoDB-compatible documents | **DocumentDB** |
  | Cassandra-compatible | **Keyspaces** |

| In a question | Answer |
|---|---|
| "reads from DynamoDB in microseconds" | DAX |
| "the same queries hit the database repeatedly" | ElastiCache in front of it |
| "relational, unpredictable load, little management" | Aurora Serverless v2 |
| "millions of requests per second, simple key lookups" | DynamoDB |

## Networking

*Practised in Compute lesson 2, Containers lessons 4-5.*

- **CloudFront** caches content at **edge locations** near users, for
  static and dynamic content. **Global Accelerator** gives **two static
  anycast IPs** and carries TCP and UDP over the AWS network to the nearest
  healthy endpoint: for non-HTTP traffic, fixed IPs, and fast Regional
  failover. It caches nothing.
- **Load balancers**:

  | | **ALB** | **NLB** | **GWLB** |
  |---|---|---|---|
  | Layer | 7: HTTP, HTTPS, gRPC | 4: TCP, UDP, TLS | 3: IP packets |
  | Strengths | routing by path and host, redirects, WAF, Cognito login, Lambda targets | **static IPs** per AZ, UDP, millions of requests per second, PrivateLink | sends traffic through firewall or inspection appliances |

- **Hybrid**: Site-to-Site **VPN**, **Direct Connect** (consistent,
  high-bandwidth), and **PrivateLink** for private access to a service in
  another VPC.

| In a question | Answer |
|---|---|
| "static content for users worldwide" | CloudFront |
| "UDP game servers, fixed IPs for allow-lists" | Global Accelerator (or NLB in one Region) |
| "route /api and /images to different services" | ALB path-based routing |

## Data ingestion and analytics

- **Streams**: **Kinesis Data Streams** for real-time streams with many
  consumers and replay; **Amazon Data Firehose** delivers a stream to S3,
  Redshift or OpenSearch with no code (near real time, buffered);
  **Managed Service for Apache Flink** processes streams.
- **Lake**: **Glue** is serverless ETL plus the **Data Catalog** of table
  definitions; **Athena** runs SQL directly on S3, cheaper and faster on
  **columnar** formats (Parquet, ORC) with **partitions**, since it reads
  less; **Lake Formation** manages data lake permissions.
- **Moving data in**:

  | Service | For |
  |---|---|
  | **DataSync** | online copies and sync from NFS, SMB, HDFS to S3, EFS, FSx |
  | **Storage Gateway** | on-premises applications using cloud storage (file, volume, tape) |
  | **Snowball Edge** | offline transfer of terabytes to petabytes, by shipped device |
  | **Transfer Family** | SFTP, FTPS, FTP endpoints writing to S3 or EFS |

| In a question | Answer |
|---|---|
| "clickstream, several apps read it, replay" | Kinesis Data Streams |
| "load streaming data into S3 with no code" | Firehose |
| "SQL on files in S3, pay per query" | Athena, with Parquet and partitions |
| "100 TB over a slow link" | Snowball Edge |

## Traps

- **Instance store** data is lost when the instance stops.
- A **cluster placement group** is in **one AZ**: fast, not highly
  available.
- **Global Accelerator does not cache**; CloudFront does.
- **Read replicas** do not speed up writes; a bigger instance, sharding or
  DynamoDB does.
- Lambda is wrong for jobs over **15 minutes**.

Source: AWS Certified Solutions Architect - Associate (SAA-C03) exam guide,
Content Domain 3; AWS service documentation.

## Questions from open banks

- 55 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
