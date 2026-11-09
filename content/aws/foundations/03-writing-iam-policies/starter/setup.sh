#!/usr/bin/env bash
# Lesson 3: writing IAM policies.
set -euo pipefail

# The bucket the analysts read from (done for you).
aws s3api create-bucket --bucket lb-reports

# 1. A customer managed policy called reports-read, from policy.json.


# 2. The analysts group, with reports-read attached.


# 3. The user carol, in analysts.

