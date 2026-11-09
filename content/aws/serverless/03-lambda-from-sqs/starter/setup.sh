#!/usr/bin/env bash
# Serverless 3: Lambda, fed by a queue.
set -euo pipefail

# Done for you: the queue, with a 120 second visibility timeout.
QUEUE_URL=$(aws sqs create-queue --queue-name orders \
  --attributes VisibilityTimeout=120 --query QueueUrl --output text)
QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url "$QUEUE_URL" \
  --attribute-names QueueArn --query Attributes.QueueArn --output text)

# 1. handler.py (edit the file).

# 2. The role process-order: trusted by lambda.amazonaws.com, with
#    AWSLambdaSQSQueueExecutionRole.


# 3. Package handler.py and create the function process-order: python3.12,
#    handler handler.handler, 20 s, 256 MB, TABLE=orders.


# 4. Reserved concurrency 10; event source mapping from orders, batch size 10,
#    ReportBatchItemFailures.

