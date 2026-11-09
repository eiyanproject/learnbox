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

A queue has one set of consumers. When several independent services each
need every order - billing, shipping, analytics - put **SNS** in front:
publish once to a **topic**, and SNS delivers a copy to every
**subscription**. With an SQS queue per consumer (the **fan-out** pattern),
each service keeps its own buffer, its own pace and its own dead-letter
queue.

## Letting the topic in

SNS delivers to a queue by calling `sqs:SendMessage` on it, so the queue's
**access policy** must allow the SNS service - and only for *your* topic,
which is what the `aws:SourceArn` condition is for:

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "sns.amazonaws.com" },
  "Action": "sqs:SendMessage",
  "Resource": "arn:aws:sqs:us-east-1:123456789012:billing",
  "Condition": { "ArnEquals": { "aws:SourceArn": "arn:aws:sns:us-east-1:123456789012:order-events" } }
}
```

## Raw delivery

Without it, each queue message is an SNS envelope (JSON with `Type`,
`MessageId`, `Message`...) around your message. **Raw message delivery**
passes just your message through - simpler for consumers.

## Filter policies

A subscription can have a **filter policy** on message attributes (or on the
message body). Shipping does not care about orders until they are paid, so
its subscription asks for `event = order_paid` only, and SNS drops the rest
for that subscriber - no code, no wasted messages.

## SNS or EventBridge?

Both fan out. **SNS** is high-throughput push to many subscribers (queues,
Lambda, HTTP, email, SMS, mobile push). **EventBridge** routes by rich rules
on event content, takes events from AWS services and SaaS partners, and can
archive and replay. Choose by what the events are and where they go.

## Your task

1. A topic **`order-events`**.
2. Queues **`billing`** and **`shipping`**, each with a policy letting
   **only that topic** send to it.
3. Subscribe both with **raw delivery**; give **shipping** a filter policy
   for `event` = **`order_paid`**.
4. Publish two messages: one with `event` = **`order_placed`**, one with
   `event` = **`order_paid`**.

Billing should end up with both, shipping with one.
