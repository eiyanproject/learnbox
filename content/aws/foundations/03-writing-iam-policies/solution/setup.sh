#!/usr/bin/env bash
# Lesson 3: writing IAM policies.
set -euo pipefail

# The bucket the analysts read from (done for you).
aws s3api create-bucket --bucket lb-reports

# 1. A customer managed policy called reports-read, from policy.json.
POLICY_ARN=$(aws iam create-policy --policy-name reports-read \
  --policy-document file://policy.json \
  --query Policy.Arn --output text)

# 2. The analysts group, with reports-read attached.
aws iam create-group --group-name analysts
aws iam attach-group-policy --group-name analysts --policy-arn "$POLICY_ARN"

# 3. The user carol, in analysts.
aws iam create-user --user-name carol
aws iam add-user-to-group --group-name analysts --user-name carol
