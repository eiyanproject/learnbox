---
title: Queues and dead letters
summary: SQS standard and FIFO queues - visibility timeout, long polling, retention, a dead-letter queue for poison messages - and sending and receiving from the CLI.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "Attributes are strings in a JSON map, and the redrive policy is JSON inside one of those strings. Rather than fight the quoting, write the file with python3: `json.dumps({..., \"RedrivePolicy\": json.dumps({\"deadLetterTargetArn\": arn, \"maxReceiveCount\": \"5\"})})`, then `--attributes file://orders-attrs.json`."
  - "A queue's ARN: `aws sqs get-queue-attributes --queue-url \"$URL\" --attribute-names QueueArn --query Attributes.QueueArn --output text`."
  - "A FIFO queue's name must end in .fifo: `aws sqs create-queue --queue-name payments.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true`."
  - "FIFO messages need a group: `aws sqs send-message --queue-url \"$PAY\" --message-body '...' --message-group-id account-1`."
---

**SQS** is a queue as a service: producers send messages, consumers
receive, process and **delete** them. It decouples the two - a slow or
failed consumer does not slow the producer down - and it scales without
anything to manage.

## How a message moves

1. A consumer **receives** a message. It is not removed - it becomes
   **invisible** for the **visibility timeout** (30 s by default).
2. If the consumer **deletes** it in time, it is gone.
3. If not - the consumer crashed, or was too slow - it becomes visible
   again and is delivered again.

So set the visibility timeout longer than processing takes, and make
processing **idempotent**: a standard queue delivers **at least once**, so a
message can occasionally arrive twice.

## Settings worth knowing

| Attribute | Default | Notes |
|---|---|---|
| `VisibilityTimeout` | 30 s | up to 12 hours |
| `ReceiveMessageWaitTimeSeconds` | 0 | 1-20 turns on **long polling**: fewer empty responses, lower cost |
| `MessageRetentionPeriod` | 4 days | 1 minute to 14 days |
| `DelaySeconds` | 0 | hold new messages back, up to 15 minutes |
| `RedrivePolicy` | none | after `maxReceiveCount` receives, move to the **dead-letter queue** |

A **dead-letter queue** (DLQ) catches the **poison messages** - the ones
that fail every time - so they stop blocking the rest and can be examined.
Give it a longer retention than the source queue, so nothing expires there
before anyone looks.

## FIFO queues

**FIFO** queues (names ending `.fifo`) give **exactly-once processing** and
**strict order within a message group**. Messages with different group IDs
are processed in parallel; messages in one group, one at a time, in order.
**Content-based deduplication** drops a message whose body matches one sent
in the last five minutes. Throughput is lower than standard queues (high
throughput mode raises it).

## Your task

1. A queue **`orders-dlq`** with **14 days** of retention (1209600 s).
2. A queue **`orders`**: visibility timeout **120**, long polling **20**,
   retention **4 days** (345600), redriving to `orders-dlq` after **5**
   receives.
3. A FIFO queue **`payments.fifo`** with **content-based deduplication**.
4. Send **two** messages to `orders`, and **one** to `payments.fifo` in the
   message group **`account-1`**.

After **Run**, receive one: `aws sqs receive-message --queue-url "$(aws sqs
get-queue-url --queue-name orders --query QueueUrl --output text)"`.
