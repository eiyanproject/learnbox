#!/usr/bin/env bash
# Lesson 6: locking down a bucket.
set -euo pipefail

aws s3api create-bucket --bucket lb-data
printf 'quarter,revenue\nq1,100\n' > report.csv

# 1. All four Block Public Access settings on.


# 2. A KMS key, alias/lb-data, with rotation on.


# 3. Default encryption: SSE-KMS with that key, Bucket Key enabled.


# 4. Upload report.csv.


# 5. The TLS-only bucket policy from bucket-policy.json - last.

