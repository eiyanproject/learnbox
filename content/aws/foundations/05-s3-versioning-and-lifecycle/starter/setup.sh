#!/usr/bin/env bash
# Lesson 5: S3 objects, versioning and lifecycle.
set -euo pipefail

aws s3api create-bucket --bucket lb-logs
echo "first line" > app.log

# 1. Versioning on for lb-logs.


# 2. app.log to logs/app.log, then change it and upload it again.


# 3. The lifecycle rule from lifecycle.json.

