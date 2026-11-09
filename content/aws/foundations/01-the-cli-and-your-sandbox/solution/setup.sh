#!/usr/bin/env bash
# Lesson 1: the CLI and your sandbox account.
# Runs against an empty account. Stop at the first failing command.
set -euo pipefail

# 1. A bucket called lb-first-bucket, in the default Region (us-east-1).
aws s3api create-bucket --bucket lb-first-bucket

# 2. Tag it project=learnbox.
aws s3api put-bucket-tagging --bucket lb-first-bucket \
  --tagging 'TagSet=[{Key=project,Value=learnbox}]'

# 3. A bucket called lb-tokyo-bucket in ap-northeast-1.
aws s3api create-bucket --bucket lb-tokyo-bucket \
  --region ap-northeast-1 \
  --create-bucket-configuration LocationConstraint=ap-northeast-1
