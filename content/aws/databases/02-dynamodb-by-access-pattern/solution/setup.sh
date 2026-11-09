#!/usr/bin/env bash
# Databases 2: DynamoDB, designed by access pattern.
set -euo pipefail

# 1. The table orders: pk (S) and sk (S), on-demand, GSI by-status on status + sk.
aws dynamodb create-table --table-name orders \
  --attribute-definitions \
    AttributeName=pk,AttributeType=S \
    AttributeName=sk,AttributeType=S \
    AttributeName=status,AttributeType=S \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --global-secondary-indexes \
    'IndexName=by-status,KeySchema=[{AttributeName=status,KeyType=HASH},{AttributeName=sk,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST \
  --query TableDescription.TableStatus --output text
aws dynamodb wait table-exists --table-name orders

# 2. TTL on expires_at; point-in-time recovery on.
aws dynamodb update-time-to-live --table-name orders \
  --time-to-live-specification Enabled=true,AttributeName=expires_at >/dev/null
aws dynamodb update-continuous-backups --table-name orders \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true >/dev/null

# 3. Write items.json (edit the file) with batch-write-item.
aws dynamodb batch-write-item --request-items file://items.json
