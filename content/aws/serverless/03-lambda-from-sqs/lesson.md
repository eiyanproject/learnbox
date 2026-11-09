---
title: Lambda, fed by a queue
summary: A function with its own execution role, packaged and deployed from the CLI, reading batches from SQS with partial-batch failure reporting - and the timeout arithmetic that keeps messages from being processed twice.
order: 3
files: [setup.sh, handler.py]
run: awslab run setup.sh
hints:
  - "The execution role trusts `lambda.amazonaws.com`. Attach the AWS managed policy `arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole` - it covers reading and deleting messages and writing logs."
  - "Package with Python's zipfile so nothing extra is needed: `python3 -c \"import zipfile; zipfile.ZipFile('function.zip','w').write('handler.py')\"`."
  - "`aws lambda create-function --function-name process-order --runtime python3.12 --handler handler.handler --role \"$ROLE_ARN\" --zip-file fileb://function.zip --timeout 20 --memory-size 256 --environment 'Variables={TABLE=orders}'`."
  - "`aws lambda create-event-source-mapping --function-name process-order --event-source-arn \"$QUEUE_ARN\" --batch-size 10 --function-response-types ReportBatchItemFailures`, and `aws lambda put-function-concurrency --function-name process-order --reserved-concurrent-executions 10`."
---

**Lambda** runs your code when something happens and bills by the
millisecond; there are no servers to keep running. A function is code plus
configuration: runtime, handler, memory (which also sets CPU), timeout (up to
15 minutes), environment variables, and an **execution role** - the
permissions the code runs with.

## Fed by a queue

With an **event source mapping**, the Lambda service polls an SQS queue
for you and invokes the function with **batches** of messages. If the
function succeeds, the messages are deleted; if it fails, the batch becomes
visible again for a retry - and after `maxReceiveCount` tries, goes to the
dead-letter queue.

Two details save a lot of grief:

- **Partial batch failures.** By default one bad message fails the whole
  batch, and the nine good ones are processed again. With
  `ReportBatchItemFailures`, the function returns the IDs of only the
  messages that failed:

  ```python
  return {"batchItemFailures": [{"itemIdentifier": msg_id}]}
  ```

- **Timeouts.** The queue's visibility timeout must exceed the function's
  timeout, or a message reappears while it is still being processed. AWS
  recommends **at least six times** the function timeout. The `orders` queue
  here has 120 seconds - so the function gets **20**.

## Concurrency

Lambda scales by running more copies at once. **Reserved concurrency** caps
one function (and guarantees it that much of the account's pool), which
protects whatever it writes to - a database that can take 10 connections
should not meet 1,000 invocations. **Provisioned concurrency** keeps copies
warm against cold starts.

## A note on this sandbox

The emulator stores the function and its configuration exactly as AWS
would, but does not run the code - that would need a container runtime. The
check reads `handler.py` itself and calls `handler()` with a sample batch.

## Your task

The script creates the queue **`orders`** (120 s visibility). Add:

1. write **`handler.py`**: a function `handler(event, context)` that reads each
   record in `event["Records"]`, parses its `body` as JSON, collects the
   `messageId` of every record whose body is not valid JSON or has no
   `"order"` key, and returns `{"batchItemFailures": [{"itemIdentifier": id},
   ...]}`;
2. a role **`process-order`** that Lambda can assume, with
   **AWSLambdaSQSQueueExecutionRole**;
3. a function **`process-order`**: python3.12, handler `handler.handler`,
   **20 s** timeout, **256 MB**, environment **TABLE=orders**;
4. **reserved concurrency of 10**, and an event source mapping from
   `orders`, **batch size 10**, with **ReportBatchItemFailures**.
