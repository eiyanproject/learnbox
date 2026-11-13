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

When a customer places an order, the web server has work to hand off:
charge the card, send the confirmation email, tell the warehouse. If it did
all of that itself before answering, every slow email server would slow the
shop down, and every failure would lose an order. Instead it can drop a
message on a **queue** and answer at once; separate workers take messages
off the queue and do the work at their own pace.

**SQS** (Simple Queue Service) is a queue as a service. **Producers** send
messages; **consumers** receive them, process them, and **delete** them.
It **decouples** the two sides: a slow or crashed consumer does not slow the
producer, messages wait safely until someone handles them, and there are no
servers to manage. This section of the course builds on that idea: queues
here, fan-out to several queues in lesson 2, Lambda functions as consumers
in lesson 3.

## How a message moves

Receiving a message does **not** remove it from the queue. This is the
part that surprises people, and everything else follows from it:

1. A consumer **receives** a message. SQS hides it from other consumers for
   the **visibility timeout** (30 seconds by default), and hands the
   consumer a **receipt handle** for it.
2. If the consumer **deletes** the message, using the receipt handle,
   before the timeout ends, it is gone for good.
3. If it does not (the consumer crashed, or took too long), the message
   becomes **visible** again, and is delivered again, to this consumer or
   another.

Here it is happening, on a queue with a 2-second visibility timeout:

```
$ aws sqs receive-message --queue-url "$U" --query 'Messages[0].Body' --output text
{"order": 1}
$ aws sqs receive-message --queue-url "$U" --query 'length(Messages || `[]`)'
0
  ... 3 seconds later, without deleting it ...
$ aws sqs receive-message --queue-url "$U" --attribute-names ApproximateReceiveCount \
    --query 'Messages[0].[Body,Attributes.ApproximateReceiveCount]' --output text
{"order": 1}	2
```

The second receive found nothing, because the message was invisible. Once
the timeout passed, the same message came back, now received twice.

Two rules follow:

- Set the visibility timeout **longer than processing takes**. Too short,
  and a message still being worked on reappears and is processed twice in
  parallel.
- Make processing **idempotent**: doing it twice must have the same effect
  as doing it once ("set order 7 to paid", not "add 10 to the balance"). A
  standard queue delivers **at least once**, so a message can occasionally
  arrive twice even when everything works.

## Settings worth knowing

Queue settings are **attributes**, all given as strings:

| Attribute | Default | Notes |
|---|---|---|
| `VisibilityTimeout` | 30 s | up to 12 hours, counted from the first receive, however often it is extended |
| `ReceiveMessageWaitTimeSeconds` | 0 | 1 to 20 turns on **long polling**: a receive waits for a message to arrive instead of returning empty at once. Fewer empty responses, and 💸 fewer paid requests |
| `MessageRetentionPeriod` | 4 days | 1 minute to 14 days; a message older than this is deleted unread |
| `DelaySeconds` | 0 | hold new messages back, up to 15 minutes |
| `MaximumMessageSize` | 1 MiB | the largest message body (raised from 256 KB in 2025); bigger payloads go to S3, with a pointer in the message |
| `RedrivePolicy` | none | after `maxReceiveCount` receives without a delete, move the message to the **dead-letter queue** |

## Dead-letter queues

Some messages fail every time: a malformed order, a customer ID that does
not exist. Without a limit, such a **poison message** is received, fails,
reappears, fails again, forever, using a consumer's time on every round.

A **dead-letter queue** (DLQ) is an ordinary queue that catches them. The
source queue's **redrive policy** names it and a `maxReceiveCount`: once a
message has been received that many times without being deleted, SQS moves
it to the DLQ instead of delivering it again. The rest of the queue flows
on, and someone can examine the dead letters (and an alarm on the DLQ's
depth tells them to, section 6).

Give the DLQ a **longer** retention than the source queue: retention counts
from when the message was first sent, so with the same period, dead letters
could expire before anyone looked.

### The quoting problem

The redrive policy is itself a JSON document, and SQS wants it as a
**string**, inside the attributes, which are also JSON:

```json
{
  "VisibilityTimeout": "120",
  "RedrivePolicy": "{\"deadLetterTargetArn\": \"arn:aws:sqs:us-east-1:123456789012:orders-dlq\", \"maxReceiveCount\": \"5\"}"
}
```

Every inner quote needs a backslash, and the ARN is only known at run time.
Rather than build that by hand in the shell, let Python's `json` module do
the quoting: `json.dumps` turns the inner policy into a string, and the
outer one into the file. A **here document** (`<<'PY' ... PY`) passes the
Python code to `python3`, and the ARN as an argument:

```bash
python3 - "$DLQ_ARN" > orders-attrs.json <<'PY'
import json, sys
print(json.dumps({
    "VisibilityTimeout": "120",
    "RedrivePolicy": json.dumps({"deadLetterTargetArn": sys.argv[1], "maxReceiveCount": "5"}),
}))
PY
aws sqs create-queue --queue-name orders --attributes file://orders-attrs.json
```

The quotes around `'PY'` stop the shell from changing anything inside. The
DLQ's ARN comes from `get-queue-attributes`, since `create-queue` only
returns the queue's **URL** (`http://.../123456789012/orders-dlq`), which
the other SQS commands use to name a queue.

## FIFO queues

A standard queue is fast but makes no promise about **order**, and may
deliver a message twice. Some work needs both guarantees: a bank account's
deposits and withdrawals must apply in order, exactly once. **FIFO** queues
(first in, first out) provide them:

| | Standard | FIFO |
|---|---|---|
| Delivery | at least once; occasionally twice | **exactly-once processing** |
| Order | best effort | **strict, within each message group** |
| Throughput | nearly unlimited | lower (thousands of messages per second with high throughput mode) |
| Name | anything | must end in **`.fifo`** |

Order is kept **per message group**: every message carries a **message group
ID**, and messages in one group are delivered one at a time, in order, while
different groups are processed in parallel. Use the account ID as the group,
and each account's payments stay in order without holding up the others.
Both requirements are enforced:

```
An error occurred (InvalidParameterValue) when calling the CreateQueue operation: Queue name must end in .fifo for FIFO queues
An error occurred (MissingParameter) when calling the SendMessage operation: The request must contain the parameter MessageGroupId.
```

A dead-letter queue and strict order do not mix well: moving a failed
message aside lets the next message in its group go first, so where the
order is the whole point, think twice before adding a DLQ to a FIFO queue.

**Content-based deduplication** makes SQS drop a message whose body matches
one sent in the previous five minutes, so a producer that retries after a
timeout does not create a duplicate payment.

## Queues in practice

- A consumer that needs more time calls **`ChangeMessageVisibility`** to
  extend the timeout for one message, instead of setting a long timeout for
  all.
- One receive returns up to **10** messages; process them, delete each.
- Consumers running on EC2 scale with an Auto Scaling group on the queue's
  length, `ApproximateNumberOfMessagesVisible`; Lambda (lesson 3) scales by
  itself.
- A queue in front of a database smooths out spikes: the application writes
  orders to the queue, and workers insert them at the pace the database can
  take, deleting each message only after the insert succeeded.
- Messages are encrypted at rest with **SSE-SQS** by default, or with your
  own KMS key; access is controlled by IAM and a queue **access policy**
  (lesson 2).

## Your task

1. A queue **`orders-dlq`** with **14 days** of retention
   (`MessageRetentionPeriod=1209600`, in seconds). Keep its ARN.
2. A queue **`orders`** with a visibility timeout of **120** seconds, long
   polling of **20** seconds, retention of **4 days** (`345600`), and a
   redrive policy to `orders-dlq` after **5** receives.
3. A FIFO queue **`payments.fifo`** with **content-based deduplication**.
4. Send **two** messages to `orders`, and **one** to `payments.fifo` in the
   message group **`account-1`**. (Each Run starts from an empty account, so
   these are the only messages.)

After **Run**, receive one:

```
aws sqs receive-message --queue-url "$(aws sqs get-queue-url --queue-name orders --query QueueUrl --output text)"
```

Thanks to long polling it returns as soon as a message is there. The answer
includes the `Body` and the `ReceiptHandle`; `aws sqs delete-message
--queue-url ... --receipt-handle ...` would remove it. Run it more than 5
times without deleting (waiting 2 minutes each time) and the message would
move to `orders-dlq`.

## Check yourself

1. A consumer crashed halfway through a message. What happens to it?
   *It becomes visible again after the visibility timeout and is delivered
   again.*
2. Why must processing be idempotent on a standard queue?
   *A message can occasionally be delivered twice.*
3. Why give the dead-letter queue a longer retention?
   *Retention counts from the original send time.*
4. What does a FIFO queue guarantee that a standard one does not?
   *Order within a message group, and exactly-once processing.*
