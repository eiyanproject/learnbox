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
ROLE_ARN=$(aws iam create-role --role-name process-order \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query Role.Arn --output text)
aws iam attach-role-policy --role-name process-order \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole

# 3. Package handler.py and create the function process-order: python3.12,
#    handler handler.handler, 20 s, 256 MB, TABLE=orders.
python3 -c "import zipfile; zipfile.ZipFile('function.zip', 'w').write('handler.py')"
aws lambda create-function --function-name process-order \
  --runtime python3.12 --handler handler.handler --role "$ROLE_ARN" \
  --zip-file fileb://function.zip --timeout 20 --memory-size 256 \
  --environment 'Variables={TABLE=orders}' \
  --query State --output text

# 4. Reserved concurrency 10; event source mapping from orders, batch size 10,
#    ReportBatchItemFailures.
aws lambda put-function-concurrency --function-name process-order \
  --reserved-concurrent-executions 10 >/dev/null
aws lambda create-event-source-mapping --function-name process-order \
  --event-source-arn "$QUEUE_ARN" --batch-size 10 \
  --function-response-types ReportBatchItemFailures \
  --query State --output text
