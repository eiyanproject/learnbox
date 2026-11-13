---
title: Fan-out with SNS
summary: One event, many consumers - an SNS topic delivering to two SQS queues, queue policies that let only that topic in, raw delivery, and a filter policy so a consumer only gets the events it wants.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "A queue policy is set as the queue's Policy attribute. The statement allows `Principal: {\"Service\": \"sns.amazonaws.com\"}` to `sqs:SendMessage` on the queue's ARN, with `\"Condition\": {\"ArnEquals\": {\"aws:SourceArn\": \"<topic ARN>\"}}`."
  - "`aws sns subscribe --topic-arn \"$TOPIC\" --protocol sqs --notification-endpoint \"$QUEUE_ARN\" --attributes '{\"RawMessageDelivery\":\"true\"}' --query SubscriptionArn --output text`."
  - "A filter policy matches message attributes: `--attributes '{\"RawMessageDelivery\":\"true\",\"FilterPolicy\":\"{\\\"event\\\":[\\\"order_paid\\\"]}\"}'` - or set it afterwards with `aws sns set-subscription-attributes --attribute-name FilterPolicy`."
  - "Publishing with an attribute: `aws sns publish --topic-arn \"$TOPIC\" --message '{\"order\":7}' --message-attributes '{\"event\":{\"DataType\":\"String\",\"StringValue\":\"order_paid\"}}'`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **SNS** | Simple Notification Service: publish once, deliver to every subscriber |
| **publish** | send a message to a topic |
| **topic** | where messages are published |
| **subscription** | one destination of a topic: a queue, a function, an HTTP endpoint, an email |
| **fan-out** | one queue per service behind a topic, so each gets every message |
| **access policy** | the queue's resource policy; must allow `sqs:SendMessage` from SNS |
| **`aws:SourceArn`** | condition limiting the permission to your topic |
| **`Policy` attribute** | how a queue's access policy is set |
| **envelope** | SNS's JSON wrapping around your message |
| **raw message delivery** | passes just your message through |
| **filter policy** | a subscription only gets messages whose attributes match |
| **message attributes** | typed key-value pairs sent alongside the body |
| **push** | the service delivers to you, instead of you polling |
| **EventBridge** | routes events by rules on their content |
| **SaaS partner** | an outside software service that sends events to EventBridge |
| **archive and replay** | EventBridge keeping events to send again later |
| **SNS FIFO topic** | ordered, deduplicated; only SQS FIFO queues subscribe |
| **stores nothing** | SNS keeps no copy, which is why queues sit behind it |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws sns create-topic --name N` | creates a topic; prints its ARN |
| `aws sns subscribe --topic-arn T --protocol sqs --notification-endpoint QUEUE_ARN --attributes '{...}'` | subscribes a queue (by ARN) |
| `"RawMessageDelivery":"true"`, `"FilterPolicy":"{\"event\":[\"order_paid\"]}"` | subscription attributes |
| `aws sqs set-queue-attributes --queue-url U --attributes file://...` | sets the queue's `Policy` |
| `aws sns publish --topic-arn T --message M --message-attributes '{"event":{"DataType":"String","StringValue":"order_paid"}}'` | publishes with an attribute |
| `sqs:SendMessage` | the action SNS needs on the queue |

### Errors

| Error | Means |
|---|---|
| *(no error at all)* | in real AWS, a queue without the access policy silently receives nothing |

---

A queue's messages are shared by its consumers: each message is handled by
**one** of them. That suits a pool of identical workers. But when several
**different** services each need **every** order (billing to invoice it,
shipping to pack it, analytics to count it), one queue is the wrong shape:
whichever service takes a message, the others never see it.

**SNS** (Simple Notification Service) solves this. A producer **publishes**
a message once to a **topic**, and SNS delivers a copy to every
**subscription** on it. Subscribe one SQS queue per service, and you have
the **fan-out** pattern: each service keeps its own queue, works at its own
pace, retries on its own, and can have its own dead-letter queue, while the
producer knows nothing about who is listening.

```text
                              ┌──> queue billing   (every event)
 producer ──publish──> topic ─┤
   order-events               └──> queue shipping  (filter: event = order_paid)
```

## Letting the topic in

SNS delivers to a queue by calling `sqs:SendMessage` on it, as an AWS
service. A queue refuses that unless its **access policy**, a resource
policy on the queue like a bucket policy (Foundations lesson 6), allows it.
And it should allow it only for **your** topic, not for any SNS topic in any
account, which is what the `aws:SourceArn` condition is for:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "sns.amazonaws.com" },
    "Action": "sqs:SendMessage",
    "Resource": "arn:aws:sqs:us-east-1:123456789012:billing",
    "Condition": { "ArnEquals": { "aws:SourceArn": "arn:aws:sns:us-east-1:123456789012:order-events" } }
  }]
}
```

Read it as "allow **the SNS service** to **send messages** to **this
queue**, **when** the message comes from the topic `order-events`".

The policy is set as the queue's `Policy` **attribute**, with
`set-queue-attributes`, and like last lesson's redrive policy it is a JSON
document inside a JSON string: the same `python3` and `json.dumps` approach
saves the quoting. Each queue's policy names its own ARN and the topic's,
both only known at run time, so a small shell function that creates a queue,
looks up its ARN, writes its policy and applies it keeps the script short.

(In real AWS, a queue without this policy silently receives nothing from
the topic, and the subscription still looks fine: a classic hour-long
puzzle. The emulator delivers anyway, so the check reads the policy
itself.)

## Subscribing

```
aws sns subscribe --topic-arn "$TOPIC" --protocol sqs \
  --notification-endpoint "$QUEUE_ARN" \
  --attributes '{"RawMessageDelivery":"true"}'
```

The endpoint of an SQS subscription is the queue's **ARN**, not its URL.
`create-topic` prints the topic's ARN, `arn:aws:sns:us-east-1:123456789012:order-events`.

### Raw delivery

By default, what arrives in the queue is not your message but an SNS
**envelope** around it, with your message as a string inside:

```json
{
    "Type": "Notification",
    "MessageId": "2aa686f7-158a-4d10-9d63-eba91634c8e5",
    "Message": "{\"order\":7}",
    "MessageAttributes": { "event": { "Type": "String", "Value": "order_paid" } },
    "Signature": "D3td91P9EEPT...",
    ...
}
```

Every consumer then has to unwrap it. **Raw message delivery**, a
subscription attribute, passes just your message through, `{"order":7}`,
with the message attributes carried as SQS message attributes.

## Filter policies

Shipping does not care about an order until it is paid. Without filtering,
it would receive every event and throw most away, paying for each one. A
subscription can have a **filter policy**, matched against the message's
**attributes** (or, optionally, its body), and SNS only delivers the
messages that match, to that subscription:

```json
{"event": ["order_paid"]}
```

means "only messages whose attribute `event` is `order_paid`" (a list, since
several values can be allowed). Other subscriptions are unaffected: billing
still gets everything. A change to a filter policy can take up to 15
minutes to take effect, so test a new filter before relying on it.

**Message attributes** are typed key-value pairs sent alongside the message
body, set when publishing:

```
aws sns publish --topic-arn "$TOPIC" --message '{"order":7}' \
  --message-attributes '{"event":{"DataType":"String","StringValue":"order_paid"}}'
```

The filter policy goes into the subscription's attributes as a **string**,
so inside the `--attributes` JSON its quotes need backslashes:
`'{"RawMessageDelivery":"true","FilterPolicy":"{\"event\":[\"order_paid\"]}"}'`.

## SNS or EventBridge?

Both deliver one event to many targets. The exam asks which fits:

| | SNS | EventBridge |
|---|---|---|
| Strength | high-throughput **push** to many subscribers | **routing by rules** on the content of events |
| Targets | SQS, Lambda, HTTP endpoints, email, SMS, mobile push | many AWS services, API destinations |
| Event sources | your own publishers | your publishers, **AWS services' own events**, SaaS partners |
| Extras | message filtering, FIFO topics | schemas, **archive and replay**, scheduling (lesson 4) |

SNS itself **stores nothing**: a message that cannot be delivered right now
can be lost. That is the other half of why fan-out puts **queues** behind
the topic: they keep each copy until its consumer is ready. (An **SNS FIFO**
topic gives ordering and deduplication too, and only accepts SQS FIFO
queues as subscribers.)

## Your task

1. A topic **`order-events`**.
2. Queues **`billing`** and **`shipping`**, each with an access policy
   allowing the SNS service (`sns.amazonaws.com`) to `sqs:SendMessage` to
   that queue, **only** from `order-events` (`aws:SourceArn`).
3. Subscribe both queues to the topic with **raw delivery**. Give
   **shipping** (only) a filter policy for `event` = **`order_paid`**;
   billing gets every event.
4. Publish two messages, each with a message attribute `event`: one with
   **`order_placed`**, one with **`order_paid`**. Put the event name in the body
   too (`{"order":7,"event":"order_paid"}`): the check looks for it there.

The check then receives from both queues: billing should hold **both**
messages, as your plain JSON (no envelope), and shipping only the
`order_paid` one. After **Run**, try it yourself:

```
aws sqs receive-message --max-number-of-messages 10 \
  --queue-url "$(aws sqs get-queue-url --queue-name shipping --query QueueUrl --output text)" \
  --query 'Messages[].Body'
```

## Check yourself

1. Why one queue per service instead of one shared queue?
   *A message on a queue goes to one consumer; each service needs its own
   copy.*
2. The shipping queue receives nothing. What do you check first?
   *Its access policy: SNS must be allowed to `sqs:SendMessage`, from this
   topic.*
3. Without raw delivery, what does the consumer receive?
   *An SNS envelope with the message as a string inside.*
4. Where does a filter policy look?
   *At the message attributes (or the body, if so configured).*
