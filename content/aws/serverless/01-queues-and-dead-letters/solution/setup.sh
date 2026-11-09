#!/usr/bin/env bash
# Serverless 1: queues and dead letters.
set -euo pipefail

# 1. orders-dlq, 14 days of retention. Keep its ARN.
DLQ_URL=$(aws sqs create-queue --queue-name orders-dlq \
  --attributes MessageRetentionPeriod=1209600 --query QueueUrl --output text)
DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ_URL" \
  --attribute-names QueueArn --query Attributes.QueueArn --output text)

# 2. orders: visibility 120, long polling 20, retention 345600, redrive to
#    orders-dlq after 5 receives. The redrive policy is JSON inside a JSON
#    string, so let python3 do the quoting.
python3 - "$DLQ_ARN" > orders-attrs.json <<'PY'
import json, sys
print(json.dumps({
    "VisibilityTimeout": "120",
    "ReceiveMessageWaitTimeSeconds": "20",
    "MessageRetentionPeriod": "345600",
    "RedrivePolicy": json.dumps({"deadLetterTargetArn": sys.argv[1], "maxReceiveCount": "5"}),
}))
PY
ORDERS_URL=$(aws sqs create-queue --queue-name orders \
  --attributes file://orders-attrs.json --query QueueUrl --output text)

# 3. payments.fifo with content-based deduplication.
PAY_URL=$(aws sqs create-queue --queue-name payments.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true \
  --query QueueUrl --output text)

# 4. Two messages to orders; one to payments.fifo in group account-1.
aws sqs send-message --queue-url "$ORDERS_URL" --message-body '{"order": 1}' >/dev/null
aws sqs send-message --queue-url "$ORDERS_URL" --message-body '{"order": 2}' >/dev/null
aws sqs send-message --queue-url "$PAY_URL" --message-body '{"payment": 1}' \
  --message-group-id account-1 >/dev/null
