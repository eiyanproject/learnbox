#!/usr/bin/env bash
# Serverless 2: fan-out with SNS.
set -euo pipefail

# 1. The topic order-events.
TOPIC=$(aws sns create-topic --name order-events --query TopicArn --output text)

# 2. Queues billing and shipping, each letting only that topic send to it.
queue() {  # name -> prints the queue ARN
  local url arn
  url=$(aws sqs create-queue --queue-name "$1" --query QueueUrl --output text)
  arn=$(aws sqs get-queue-attributes --queue-url "$url" \
    --attribute-names QueueArn --query Attributes.QueueArn --output text)
  python3 - "$arn" "$TOPIC" > "$1-policy.json" <<'PY'
import json, sys
queue, topic = sys.argv[1], sys.argv[2]
print(json.dumps({"Policy": json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "sns.amazonaws.com"},
        "Action": "sqs:SendMessage",
        "Resource": queue,
        "Condition": {"ArnEquals": {"aws:SourceArn": topic}},
    }],
})}))
PY
  aws sqs set-queue-attributes --queue-url "$url" --attributes "file://$1-policy.json"
  echo "$arn"
}
BILLING=$(queue billing)
SHIPPING=$(queue shipping)

# 3. Subscribe both with raw delivery; shipping filters on event = order_paid.
aws sns subscribe --topic-arn "$TOPIC" --protocol sqs --notification-endpoint "$BILLING" \
  --attributes '{"RawMessageDelivery":"true"}' >/dev/null
aws sns subscribe --topic-arn "$TOPIC" --protocol sqs --notification-endpoint "$SHIPPING" \
  --attributes '{"RawMessageDelivery":"true","FilterPolicy":"{\"event\":[\"order_paid\"]}"}' >/dev/null

# 4. Publish order_placed, then order_paid (as the message attribute event).
for event in order_placed order_paid; do
  aws sns publish --topic-arn "$TOPIC" --message "{\"order\":7,\"event\":\"$event\"}" \
    --message-attributes "{\"event\":{\"DataType\":\"String\",\"StringValue\":\"$event\"}}" >/dev/null
done
