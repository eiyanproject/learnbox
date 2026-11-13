---
title: "Domain 4: Troubleshooting and optimization"
summary: 18% of the exam. Finding out why with logs, metrics and traces, instrumenting code so the next problem is quicker to find, and tuning concurrency, memory and caching.
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
| **root cause analysis** | finding what really caused a failure |
| **observability** | being able to see what a system is doing from outside |
| **instrumenting** | adding logs, metrics and traces to code |
| **logs**, **metrics**, **traces** | detail / numbers over time / one request's path across services |
| **Logs Insights** | queries CloudWatch Logs |
| **structured logging** | one JSON event per line, with fields such as a request ID |
| **metric filter** | turns log patterns into a metric, for new events only |
| **`Invocations`**, **`Errors`**, **`Throttles`**, **`Duration`**, **`ConcurrentExecutions`** | Lambda's metrics |
| **`IteratorAge`** | how far behind a stream consumer is |
| **`PutMetricData`** | publishes a custom metric |
| **embedded metric format (EMF)** | a JSON log line CloudWatch turns into a metric |
| **AWS X-Ray** | traces requests and draws a service map |
| **ADOT** | AWS Distro for OpenTelemetry |
| **service map** | a picture of services and the calls between them |
| **annotation** / **metadata** | indexed, searchable trace data / extra, not indexed |
| **active tracing** | Lambda's X-Ray switch |
| **504** | gateway timeout: the integration took too long |
| **202** | accepted: work queued, answer later |
| **parallelization factor** | how many batches per Kinesis shard Lambda processes at once |
| **reserved** / **provisioned concurrency** | guarantees and caps / keeps environments ready (costs while idle) |
| **cold start** | the delay while a new environment loads |
| **SnapStart** | restores a snapshot for faster starts (Java, Python, .NET) |
| **Lambda Power Tuning** | a tool measuring cost and speed at each memory setting |
| **cache key** | what makes a different cached copy; keep it small |
| **hit rate** | the share of requests served from cache |

### Errors

| Error | Means |
|---|---|
| `TooManyRequestsException` (429) | a Lambda concurrency limit was reached |
| `ProvisionedThroughputExceededException` | a hot key or too little DynamoDB capacity |
| `502` / `504` from API Gateway | malformed proxy response / integration timed out |
| `AccessDenied` | the execution role lacks a permission |

---

When something breaks in a distributed application, the question is
**where**: the API, the function, the queue, or the table? This domain is
about finding out quickly with **logs**, **metrics** and **traces**,
instrumenting code so the next problem is quicker to find, and then making
it faster or cheaper.

**Weight: 18% of the scored questions.** Three tasks: root cause analysis,
instrumenting for observability, and optimizing.

## Seeing what happened

*Practised in Operations lesson 1.*

| Signal | Answers | AWS |
|---|---|---|
| **Logs** | what happened, in detail | CloudWatch Logs, **Logs Insights** queries |
| **Metrics** | how much, how often, how fast, over time | CloudWatch metrics and alarms |
| **Traces** | where one request spent its time, across services | **AWS X-Ray**, ADOT (OpenTelemetry) |

- **Logs**: write **structured JSON** logs (one event per line, with a
  request ID), so Logs Insights can filter and aggregate fields. **Metric
  filters** turn log patterns into metrics, for new log events only.
- **Metrics**: Lambda publishes `Invocations`, `Errors`, `Throttles`,
  `Duration`, `ConcurrentExecutions`, and for streams `IteratorAge` (how far
  behind the consumer is). Custom metrics: `PutMetricData`, or the
  **embedded metric format** (EMF), a JSON log line in a special shape that
  CloudWatch turns into a metric, with no API call slowing the request.
- **Traces**: X-Ray follows a request through API Gateway, Lambda, DynamoDB
  and others, and draws a **service map**. **Annotations** are indexed
  key-value pairs you can **search** traces by (`customer_id`);
  **metadata** is extra data that is **not** indexed. Lambda needs
  **active tracing** on, and its role X-Ray write permissions.

## Common failures

| Symptom | Usual cause | Fix |
|---|---|---|
| Lambda `TooManyRequestsException` (429) | a concurrency limit: the account's or the function's reserved concurrency | raise the limit, reserve concurrency, queue the work |
| API Gateway **502** | the Lambda proxy response is malformed | return `statusCode`, `headers`, string `body` |
| API Gateway **504** | the integration took longer than the timeout | make the work asynchronous (queue it, return 202) |
| DynamoDB `ProvisionedThroughputExceededException` | a hot key, or too little capacity | backoff, on-demand capacity, a better partition key |
| Kinesis `IteratorAge` rising | the consumer is too slow | more shards, parallelization factor, faster code |
| SQS messages processed twice | visibility timeout shorter than processing | raise it; make consumers idempotent |
| Lambda times out calling AWS services from a VPC | no route out | a NAT gateway or VPC endpoints |
| `AccessDenied` in a function | the execution role lacks the permission | add it to the role (check CloudTrail for the denied call) |

## Optimizing

*Practised in Serverless lesson 3.*

- **Concurrency**: **reserved** concurrency both guarantees and caps a
  function's share; **provisioned** concurrency keeps environments
  initialized, removing **cold starts** (the delay while a new environment
  loads your code), at a cost; **SnapStart** restores a snapshot of an
  initialized environment for faster starts on supported runtimes (Java,
  Python, .NET).
- **Memory**: more memory means more CPU, so a function can finish faster
  and cost the same or less. The cheapest setting is often **not** the
  smallest: measure (Lambda Power Tuning, Compute Optimizer).
- **Caching**: ElastiCache, DAX, API Gateway caching, CloudFront. Keep
  CloudFront's **cache key** to the headers, cookies and query strings that
  really change the response; everything else in it lowers the hit rate.
- **SNS filter policies** stop consumers being invoked for messages they
  would throw away.

| In a question | Answer |
|---|---|
| "find which service makes requests slow" | X-Ray traces and the service map |
| "search traces by customer ID" | X-Ray annotations |
| "custom metrics without slowing the function" | embedded metric format |
| "first request after idle is slow" | provisioned concurrency (or SnapStart) |
| "one function starves the others of concurrency" | reserved concurrency |

## Traps

- **Metadata** is not searchable in X-Ray; **annotations** are.
- Metric filters do not apply to old log events.
- **502** and **504** have different causes: format versus time.
- Provisioned concurrency costs money while idle; reserved concurrency
  does not.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 4; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
