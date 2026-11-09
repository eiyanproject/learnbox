#!/usr/bin/env bash
# Lesson 6: locking down a bucket.
set -euo pipefail

aws s3api create-bucket --bucket lb-data
printf 'quarter,revenue\nq1,100\n' > report.csv

# 1. All four Block Public Access settings on.
aws s3api put-public-access-block --bucket lb-data \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# 2. A KMS key, alias/lb-data, with rotation on.
KEY_ID=$(aws kms create-key --description "lb-data bucket key" \
  --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/lb-data --target-key-id "$KEY_ID"
aws kms enable-key-rotation --key-id "$KEY_ID"

# 3. Default encryption: SSE-KMS with that key, Bucket Key enabled.
aws s3api put-bucket-encryption --bucket lb-data \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/lb-data"
      },
      "BucketKeyEnabled": true
    }]
  }'

# 4. Upload report.csv.
aws s3 cp report.csv s3://lb-data/report.csv

# 5. The TLS-only bucket policy from bucket-policy.json - last.
aws s3api put-bucket-policy --bucket lb-data --policy file://bucket-policy.json
