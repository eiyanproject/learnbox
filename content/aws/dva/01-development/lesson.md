---
title: "Domain 1: Development with AWS services"
summary: 32% of the exam. Writing code for AWS - Lambda's configuration and failure handling, messaging and streaming, APIs, and DynamoDB keys, capacity and consistency.
order: 1
kind: quiz
---

**Weight: 32% of the scored questions** - the largest domain. Three tasks:
code for applications hosted on AWS, code for Lambda, and data stores.

## Lambda

- Configuration: memory (128 MB-10 GB, CPU scales with it), timeout (up to
  15 minutes), environment variables, **layers** (shared libraries, up to 5),
  **extensions**, ephemeral `/tmp` (up to 10 GB).
- **Invocation types**: synchronous (API Gateway, the SDK's
  `RequestResponse`: the caller gets the error), **asynchronous** (S3, SNS,
  EventBridge: Lambda retries twice, then sends the event to an **on-failure
  destination** or a **dead-letter queue**), and **event source mappings**
  (SQS, Kinesis, DynamoDB Streams: Lambda polls; batches, retries, bisecting).
- **Destinations** (on success / on failure) carry the event *and* the result
  or error; a DLQ carries only the event.
- In a **VPC**, a function gets ENIs in your subnets and no public IP: it
  reaches the internet through a NAT gateway, AWS services through endpoints.
- Packaging: .zip (50 MB zipped to upload directly, 250 MB unzipped) or a
  **container image** (up to 10 GB).

## Messaging and streaming

- **SQS**: long polling (`WaitTimeSeconds` up to 20), visibility timeout,
  DLQs, FIFO with `MessageGroupId` and deduplication. At-least-once on
  standard queues: make consumers **idempotent**.
- **SNS** fan-out and filter policies; **EventBridge** buses and rules;
  **Kinesis Data Streams**: ordering per **partition key** within a shard,
  replay, many consumers.
- **Step Functions**: **Standard** (up to a year, exactly-once, audit
  history) or **Express** (high volume, up to 5 minutes, at-least-once).

## APIs

- **API Gateway**: REST or HTTP APIs; **request validation** against models;
  mapping templates; **Lambda proxy integration** expects
  `{statusCode, headers, body}` - anything else is a 502.
- SDKs: retries with **exponential backoff and jitter** built in; **paginators**
  for `NextToken`; **presigned URLs** for temporary S3 access.

## DynamoDB

- **Partition key** with high cardinality spreads load; a hot key throttles.
- **Query** reads one partition by key (cheap); **Scan** reads everything.
- **Consistency**: eventually consistent by default; `ConsistentRead=true`
  for strongly consistent reads (not on GSIs).
- Capacity units: **1 RCU** = one strongly consistent read per second of up
  to **4 KB** (or two eventually consistent); **1 WCU** = one write per
  second of up to **1 KB**. Round item size *up*.
- **Conditional writes** (optimistic locking with a version attribute),
  **transactions** (`TransactWriteItems`), **Streams**, **TTL**, **DAX**.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 1; AWS service documentation.
