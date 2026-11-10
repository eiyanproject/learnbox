#!/usr/bin/env bash
# Containers 1: ECR repositories.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# 1. orders-api: immutable tags, scan on push, KMS encryption.


# 2. Lifecycle: (1) untagged after 7 days, (2) keep 20 release- images.


# 3. Repository policy ProdPull: account 111122223333 may pull.


# 4. Replicate the registry to eu-west-1 in this account.

