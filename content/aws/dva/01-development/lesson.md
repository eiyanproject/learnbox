---
title: "Domain 1: Development with AWS services"
summary: 32% of the exam. Writing code for AWS - Lambda's configuration and failure handling, messaging and streaming, APIs, and DynamoDB keys, capacity and consistency.
order: 1
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **DVA-C02** | the AWS Certified Developer - Associate exam |
| **qualifier** | the phrase that picks one answer: "MOST efficient", "LEAST code changes" |
| **Lambda layer** | shared libraries or runtimes, up to 5 per function |
| **Lambda extension** | a companion process, such as for monitoring or secrets caching |
| **ephemeral storage** | `/tmp`: 512 MB to 10 GB; never rely on it surviving |
| **synchronous invocation** | the caller waits and gets the error |
| **asynchronous invocation** | Lambda queues the event and retries twice |
| **on-failure destination** | receives a failed async event with the error |
| **destination** | where Lambda sends the event and its result or error |
| **DLQ** | receives only the failed event |
| **event source mapping** | Lambda polls SQS, Kinesis or DynamoDB Streams and invokes with batches |
| **bisect a batch** | split a failing stream batch to find the bad record |
| **execution environment** | the container a function runs in; code outside the handler runs once per environment |
| **long polling** | `WaitTimeSeconds` up to 20: wait for messages instead of returning empty |
| **idempotent** | processing twice gives the same result |
| **deduplication ID** | FIFO drops repeats with the same ID within 5 minutes |
| **Kinesis Data Streams** | ordered per partition key within a shard; replay for 24 h to a year |
| **shard** | one ordered piece of a Kinesis stream |
| **Standard** / **Express** workflow | Step Functions: up to a year, exactly once / up to 5 minutes, at least once |
| **REST API** / **HTTP API** | API Gateway types: more features / simpler and cheaper |
| **request validation** | rejects bad input against a model before your code runs |
| **Lambda proxy integration** | the function returns `statusCode`, `headers` and a string `body`, or the client gets 502 |
| **502** | bad gateway: the backend's answer was malformed |
| **exponential backoff and jitter** | retry waits that grow, with randomness; SDKs do it for you |
| **transient error** | a failure that may succeed on retry |
| **paginator** | an SDK helper that follows `NextToken` through pages |
| **presigned URL** | temporary access to one S3 object for someone without credentials |
| **cardinality** | how many distinct values a key has |
| **hot partition** | a partition most requests hit; it throttles |
| **`Query`** / **`Scan`** | read by key, cheap / read everything, pay for everything |
| **eventually** / **strongly consistent** | may miss a recent write / always latest, twice the cost, not on GSIs |
| **`ConsistentRead=true`** | asks for a strongly consistent read |
| **RCU** / **WCU** | one strong 4 KB read (or two eventual) / one 1 KB write per second; sizes round up |
| **conditional write** | write only if a condition holds, such as `version` unchanged |
| **optimistic locking** | detecting conflicting updates with a version attribute |
| **`TransactWriteItems`** | several writes all or nothing |
| **DynamoDB Streams**, **TTL**, **DAX** | change stream / free expiry / read cache |

### Errors

| Error | Means |
|---|---|
| `ConditionalCheckFailedException` | a conditional write's condition was false |
| `502` from API Gateway | the Lambda proxy response is in the wrong shape |

---

This page reviews the first domain of the **AWS Certified Developer -
Associate** exam (DVA-C02), followed by practice questions. Where the
Solutions Architect exam asks "which service?", this one asks "how does it
behave in code?": what a function does with a failed event, what an SDK
call returns, how many capacity units a read costs. Each section names the
hands-on lessons where you used what it describes.

**Weight: 32% of the scored questions**, the largest domain. Three tasks:
code for applications hosted on AWS, code for Lambda, and data stores.

## How a question is built

The exam has 65 questions in 130 minutes (15 unscored, unmarked), passes at
720 of 1000, and does not penalize wrong answers. A question is a short
story, requirements, and a **qualifier** ("MOST efficient", "LEAST code
changes", "with the LEAST operational overhead"). Read the last sentence
first, cross out every option that misses a requirement, then prefer the
**built-in** feature over code you would write: a Lambda destination over a
custom retry loop, SDK paginators over hand-made `NextToken` handling.

## Lambda

*Practised in Serverless lesson 3, CI/CD lesson 2.*

**Configuration** you set per function:

| Setting | Range and effect |
|---|---|
| Memory | 128 MB to 10 GB; **CPU grows with it** |
| Timeout | up to **15 minutes** |
| Environment variables | configuration, encrypted at rest |
| **Layers** | shared libraries or runtimes, up to 5 per function |
| **Extensions** | companion processes (monitoring, secrets caching) |
| Ephemeral storage `/tmp` | 512 MB by default, up to 10 GB; may survive between invocations of the same environment, never rely on it |

**How the function is invoked** decides who sees an error and who retries:

| Invocation | Examples | On error |
|---|---|---|
| **Synchronous** | API Gateway, ALB, the SDK's `RequestResponse` | the **caller** gets the error and decides whether to retry |
| **Asynchronous** | S3 events, SNS, EventBridge | Lambda queues the event and **retries twice**, then sends it to an **on-failure destination** or a **dead-letter queue** |
| **Event source mapping** | SQS, Kinesis, DynamoDB Streams | Lambda **polls** and invokes with **batches**; failures retry the batch; streams can **bisect** a failing batch, SQS can report partial failures |

A **destination** receives the event **and** the result or error, and can
be used for success too; a **DLQ** receives only the failed event. Prefer
destinations for new code.

- **Code outside the handler** (SDK clients, database connections) runs
  once per execution environment and is reused by later invocations: create
  clients there, not inside the handler.
- **In a VPC**, the function gets network interfaces in your subnets and
  **no public IP**: it reaches the internet through a NAT gateway, and AWS
  services through VPC endpoints. A function in a VPC that times out calling
  S3 usually lacks one of those.
- **Packaging**: a .zip (50 MB zipped for direct upload, 250 MB unzipped
  including layers), or a **container image** of up to 10 GB from ECR.

## Messaging and streaming

*Practised in Serverless lessons 1, 2 and 4.*

- **SQS**: **long polling** (`WaitTimeSeconds` up to 20) waits for messages
  instead of returning empty at once, which cuts empty responses and cost.
  The **visibility timeout** must exceed the processing time. Standard
  queues deliver **at least once**, so consumers must be **idempotent**
  (processing a message twice gives the same result, for example by
  remembering processed IDs). **FIFO** queues order by `MessageGroupId` and
  drop duplicates by **deduplication ID** (or content hash) within 5
  minutes.
- **SNS** fan-out, with **filter policies** so each subscriber gets only
  the messages it wants; **EventBridge** buses and rules match on event
  content.
- **Kinesis Data Streams** keeps records in order **per partition key**
  within a **shard**, keeps them for replay (24 hours by default, up to a
  year), and lets many consumers read the same stream.
- **Step Functions** comes in two types:

  | | **Standard** | **Express** |
  |---|---|---|
  | Duration | up to a year | up to 5 minutes |
  | Execution | exactly once, with full history | at least once (asynchronous) |
  | For | long business workflows, human approval | high-volume event processing |

## APIs and SDKs

- **API Gateway**: **REST APIs** (more features: request validation, usage
  plans and API keys, caching) or **HTTP APIs** (simpler, cheaper, lower
  latency). **Request validation** against a model rejects bad input before
  your code runs. With **Lambda proxy integration**, the function must
  return `{"statusCode": ..., "headers": {...}, "body": "..."}` with `body`
  a **string**; anything else gives the client a **502**. Integrations time
  out after **29 seconds** by default.
- **SDKs** retry throttling and transient errors with **exponential backoff
  and jitter** by themselves; **paginators** follow `NextToken` for you.
- **Presigned URLs** give someone without AWS credentials temporary access
  to one S3 object (upload or download), signed with your credentials and
  limited in time.

## DynamoDB

*Practised in Databases lesson 2.*

- The **partition key** decides which partition stores an item. A key with
  many distinct values (high cardinality, such as a user ID) spreads load;
  a key most requests share (a date, a status) creates a **hot partition**
  that throttles.
- **Query** reads items with one partition key (optionally a range of sort
  keys): cheap. **Scan** reads the whole table and filters afterwards: you
  pay for everything read.
- **Consistency**: reads are **eventually consistent** by default (may miss
  a write from the last second); `ConsistentRead=true` gives **strongly
  consistent** reads, at twice the cost, and is **not available on global
  secondary indexes**.
- **Capacity units**, rounding the item size **up**:

  | Unit | Buys, per second |
  |---|---|
  | **1 RCU** | one strongly consistent read of up to **4 KB**, or **two** eventually consistent ones |
  | **1 WCU** | one write of up to **1 KB** |

  Example: reading 10 items of 6 KB per second, strongly consistent: 6 KB
  rounds up to 8 KB = 2 RCU each, so 20 RCU (10 if eventually consistent).
  Writing them: 6 WCU each, 60 WCU.
- **Conditional writes** make optimistic locking: write only if `version`
  still equals what you read, otherwise `ConditionalCheckFailedException`.
  **Transactions** (`TransactWriteItems`) change several items all or
  nothing. **Streams** emit every change for Lambda to process; **TTL**
  deletes expired items for free; **DAX** caches reads.

| In a question | Answer |
|---|---|
| "process each failed async event later, with the error" | an on-failure destination |
| "messages are sometimes processed twice" | idempotent consumers (and check the visibility timeout) |
| "API returns 502 from a Lambda proxy" | the function's response format |
| "two users overwrite each other's updates" | conditional writes with a version attribute |
| "read your own write immediately" | `ConsistentRead=true` on the table (not a GSI) |

## Traps

- Asynchronous invocations are retried **by Lambda**; synchronous ones are
  not.
- **Scan** with a filter still consumes capacity for every item read.
- `ConsistentRead` does not work on a **GSI**.
- Capacity math **rounds up** per item: a 1.5 KB write is 2 WCU.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 1; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
