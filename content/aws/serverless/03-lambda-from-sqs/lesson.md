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

Lesson 1's queue needs a consumer: something that receives the orders,
processes them and deletes them. That could be a fleet of servers polling
the queue, which you would have to size, patch and keep running even at 3
a.m. when no orders arrive. **Lambda** removes all of that: you give it a
function, and it runs the function when there is work, as many copies at
once as needed, and bills by the millisecond of running time. No orders, no
cost.

A Lambda **function** is your code plus its configuration:

| Setting | Means |
|---|---|
| **runtime** | the language and version, such as `python3.12` |
| **handler** | which function in your code to call: `handler.handler` is the function `handler` in the file `handler.py` |
| **memory** | 128 MB to 10 GB; it also sets the CPU power, in proportion |
| **timeout** | the longest one call may run, up to 15 minutes; after that it is stopped |
| **environment variables** | configuration the code reads, such as a table name |
| **execution role** | the IAM role the code runs as: its permissions |

The execution role is lesson 4 of Foundations again: a role whose trust
policy lets the **Lambda service** (`lambda.amazonaws.com`) assume it, and
whose permissions policy says what the code may do. Here an AWS managed
policy covers it: `AWSLambdaSQSQueueExecutionRole` allows reading and
deleting messages from SQS and writing logs to CloudWatch.

## Fed by a queue

With an **event source mapping**, the Lambda service itself polls an SQS
queue for you, and calls the function with a **batch** of messages:

```text
 queue orders ──polled by Lambda──> process-order(event = up to 10 messages)
     ▲                                 │  succeeded: Lambda deletes the messages
     └── failed: messages reappear ────┘  after the visibility timeout; after
                                          maxReceiveCount tries, to the dead-letter queue
```

The `event` your handler receives looks like this (shortened):

```json
{
  "Records": [
    { "messageId": "m1", "receiptHandle": "...", "body": "{\"order\": 1}",
      "attributes": { "ApproximateReceiveCount": "1" }, "eventSource": "aws:sqs" },
    { "messageId": "m2", "receiptHandle": "...", "body": "not json at all", ... }
  ]
}
```

Each record's `body` is the message as a **string**; parse it with
`json.loads` to get the data.

### Partial batch failures

By default the batch succeeds or fails as a whole. If one message of ten is
bad and the function raises an error, all ten reappear and are processed
**again**, nine of them for nothing, and again on every retry, until the bad
one reaches the dead-letter queue.

With **`ReportBatchItemFailures`** turned on in the mapping, the function
instead returns the IDs of only the messages that failed:

```python
return {"batchItemFailures": [{"itemIdentifier": "m2"}]}
```

Lambda deletes the rest, and only `m2` is retried. An empty list,
`{"batchItemFailures": []}`, means everything succeeded. But if the
function **raises** an exception instead of returning, the whole batch
counts as failed again, even with the setting on: catch errors per record,
and return.

A sketch of the handler's shape, to fill in:

```python
def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            ...                                  # check it, process it
        except ValueError:                       # json.loads raises it for bad JSON
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
```

A body that is valid JSON but not an object (`"5"`, say) makes `"order" in
body` raise `TypeError`, so catch that too. Raising your own `ValueError`
for "no order key" lets one `except` handle every kind of bad message.

### The timeout arithmetic

The queue's **visibility timeout** (lesson 1) must be longer than the
function's **timeout**, or a message reappears while a function is still
processing it, and a second copy of the function processes it too. AWS
recommends **at least six times** the function timeout, to leave room for
Lambda's own retries. The `orders` queue has a 120-second visibility
timeout, so the function may take at most 120 / 6 = **20** seconds. (With
a batching window, which makes Lambda wait to collect a fuller batch, the
window's length is added: six times the function timeout plus the
window.)

## Concurrency

Lambda scales by running more copies of the function at once, one per
batch. That is the point, and also a danger: a database that accepts 10
connections should not meet 1,000 simultaneous invocations after a sale
fills the queue. Two settings control it:

- **Reserved concurrency** caps one function at a number of copies, and
  also guarantees it that much of the account's shared pool (1,000 per
  Region by default), so it is both a floor and a ceiling. With 10, at most
  10 batches are processed at once; the rest of the messages wait safely in
  the queue. Setting it to 0 stops the function entirely, a quick emergency
  brake. For an SQS mapping, keep it at 5 or more, or the polling itself is
  throttled. It costs nothing.
- **Provisioned concurrency** keeps copies initialised and ready, so that
  calls avoid a **cold start**, the extra delay while Lambda loads a new
  copy's runtime and code. It costs money even when idle.

## Packaging and deploying

The code is uploaded as a **zip file**. Python's standard `zipfile` module
makes one with nothing else installed:

```
python3 -c "import zipfile; zipfile.ZipFile('function.zip', 'w').write('handler.py')"
aws lambda create-function --function-name process-order \
  --runtime python3.12 --handler handler.handler --role "$ROLE_ARN" \
  --zip-file fileb://function.zip ...
```

Note **`fileb://`**, not `file://`: the `b` is for binary. With `file://`,
the CLI tries to read the zip as text and stops:

```
Error parsing parameter '--zip-file': Unable to load paramfile (function.zip), text contents could not be decoded.  If this is a binary file, please use the fileb:// prefix instead of the file:// prefix.
```

`--environment 'Variables={TABLE=orders}'` sets the environment variable,
which the code reads as `os.environ["TABLE"]`.

## A note on this sandbox

The emulator stores the function and its configuration exactly as AWS
would, but does not **run** the code (that would need a container runtime
in the box). So the check reads your `handler.py` itself and calls
`handler()` directly with sample batches.

## Lambda's limits

| Limit | Value |
|---|---|
| Memory | 128 MB to 10 GB |
| Longest run | 15 minutes |
| Environment variables | 4 KB in total |
| Temporary disk (`/tmp`) | up to 10 GB |
| Package size | 50 MB zipped, 250 MB unzipped (or a container image up to 10 GB) |
| Concurrent executions | 1,000 per Region by default, **shared by every function** in the account |

A job needing more than these (an hour of work, 30 GB of memory) belongs on
ECS or EC2. The shared pool is why reserved concurrency matters: one busy
function can otherwise starve all the others, which then get throttled
(`429 TooManyRequestsException` for direct calls).

Provisioned concurrency only works on a published **version** or **alias**,
not on `$LATEST`. For Java, Python and .NET, **SnapStart** cuts cold starts
without its cost, by starting copies from a saved snapshot.

## Your task

The script creates the queue **`orders`**, with a 120-second visibility
timeout, and its ARN in `QUEUE_ARN`. Add:

1. **`handler.py`**: a function `handler(event, context)` that goes through
   every record in `event["Records"]`, parses its `body` as JSON, and
   collects the `messageId` of every record whose body is **not valid JSON**,
   or has **no `"order"` key**. It returns
   `{"batchItemFailures": [{"itemIdentifier": id}, ...]}`, with an empty list
   when nothing failed. The check feeds it a batch where `m1` and `m4` are
   good, `m2` is not JSON and `m3` has no `order`, and expects exactly `m2`
   and `m3` back.
2. A role **`process-order`** that Lambda can assume, with
   **AWSLambdaSQSQueueExecutionRole** attached and nothing else.
3. A function **`process-order`** running as that role: runtime
   **python3.12**, handler **`handler.handler`**, a **20**-second timeout,
   **256** MB of memory, and the environment variable **TABLE=orders**.
4. **Reserved concurrency of 10**, and an event source mapping from
   `orders` with a **batch size of 10** and **ReportBatchItemFailures**.

After **Run**, `aws lambda get-function-configuration --function-name
process-order` shows the configuration, and `aws lambda
list-event-source-mappings --function-name process-order` the mapping, with
its `State` `Enabled`. Try your handler locally too:

```
python3 -c 'import handler; print(handler.handler({"Records": [{"messageId": "m2", "body": "oops"}]}, None))'
```

## Check yourself

1. Why is the function timeout 20 seconds?
   *The queue's visibility timeout, 120 s, should be at least six times
   it.*
2. Without `ReportBatchItemFailures`, one bad message fails a batch of ten.
   What happens to the nine good ones?
   *They are processed again.*
3. What does reserved concurrency of 10 protect?
   *Whatever the function writes to, and the other functions' share of the
   account pool.*
4. Why `fileb://` and not `file://` for the zip?
   *The zip is binary; `file://` reads text.*
