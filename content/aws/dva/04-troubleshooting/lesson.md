---
title: "Domain 4: Troubleshooting and optimization"
summary: 18% of the exam. Finding out why with logs, metrics and traces, instrumenting code so the next problem is quicker to find, and tuning concurrency, memory and caching.
order: 4
kind: quiz
---

**Weight: 18% of the scored questions.** Three tasks: root cause analysis,
instrumenting for observability, and optimizing.

## Seeing what happened

- **Logs**: structured JSON logs (one event per line, with request IDs) make
  **CloudWatch Logs Insights** queries easy; **metric filters** turn log
  patterns into metrics.
- **Metrics**: Lambda publishes Invocations, Errors, Throttles, Duration,
  ConcurrentExecutions, IteratorAge. Custom metrics: `PutMetricData`, or the
  **embedded metric format (EMF)** - a JSON log line that CloudWatch turns
  into a metric, with no API call in the request path.
- **Traces**: **AWS X-Ray** (and the OpenTelemetry-based ADOT) follows a
  request across services. **Annotations** are indexed key-value pairs you
  can filter traces by; **metadata** is not indexed. Lambda needs **active
  tracing** turned on.

## Common failures

| Symptom | Usual cause |
|---|---|
| Lambda `TooManyRequestsException` (429) | concurrency limit - account or reserved |
| API Gateway 502 | malformed Lambda proxy response |
| API Gateway 504 | integration timeout - make it asynchronous |
| DynamoDB `ProvisionedThroughputExceededException` | hot key or too little capacity - backoff, on-demand, better key |
| Kinesis `IteratorAge` rising | consumer too slow - more shards, parallelization, faster code |
| SQS messages processed twice | visibility timeout shorter than processing |

## Optimizing

- **Concurrency**: reserved (cap and guarantee), provisioned (pre-warmed, no
  cold starts); **SnapStart** for faster cold starts on supported runtimes.
- **Memory**: more memory means more CPU; the cheapest setting is often not
  the smallest - measure (Lambda Power Tuning, Compute Optimizer).
- **Caching**: ElastiCache, DAX, API Gateway caching, CloudFront - and keep
  CloudFront's **cache key** to the headers, cookies and query strings that
  really change the response.
- **SNS filter policies** stop consumers being invoked for messages they
  would discard.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 4; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
