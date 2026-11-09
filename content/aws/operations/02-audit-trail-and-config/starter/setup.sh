#!/usr/bin/env bash
# Operations 2: an audit trail and config rules.
set -euo pipefail

# Done for you: the two buckets and the role Config records with.
aws s3api create-bucket --bucket lb-audit-trail >/dev/null
aws s3api create-bucket --bucket lb-audit-config >/dev/null
CONFIG_ROLE=$(aws iam create-role --role-name config-recorder --assume-role-policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"config.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query Role.Arn --output text)
aws iam attach-role-policy --role-name config-recorder \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWS_ConfigRole

# 1. trail-bucket-policy.json (edit the file), applied to lb-audit-trail.


# 2. The trail org-trail: multi-Region, log file validation, started.


# 3. Config: recorder default (all supported, global too), delivery channel
#    to lb-audit-config, recorder started.


# 4. Managed rules s3-versioning (S3_BUCKET_VERSIONING_ENABLED) and
#    ebs-encrypted (ENCRYPTED_VOLUMES).

