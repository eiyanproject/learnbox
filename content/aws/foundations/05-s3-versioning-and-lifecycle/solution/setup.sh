#!/usr/bin/env bash
# Lesson 5: S3 objects, versioning and lifecycle.
set -euo pipefail

aws s3api create-bucket --bucket lb-logs
echo "first line" > app.log

# 1. Versioning on for lb-logs.
aws s3api put-bucket-versioning --bucket lb-logs \
  --versioning-configuration Status=Enabled

# 2. app.log to logs/app.log, then change it and upload it again.
aws s3 cp app.log s3://lb-logs/logs/app.log
echo "second line" >> app.log
aws s3 cp app.log s3://lb-logs/logs/app.log

# 3. The lifecycle rule from lifecycle.json.
aws s3api put-bucket-lifecycle-configuration --bucket lb-logs \
  --lifecycle-configuration file://lifecycle.json
