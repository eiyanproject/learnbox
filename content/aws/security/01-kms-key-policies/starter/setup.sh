#!/usr/bin/env bash
# Security 1: KMS key policies and envelope encryption.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# 1. Roles orders-app and reporting (trusted by ec2.amazonaws.com) and
#    key-admin (trusted by the account).


# 2. A key "orders data" with a three-statement key policy:
#    account delegation, key-admin (admin actions only), orders-app
#    (Encrypt, Decrypt, GenerateDataKey*, DescribeKey when app=orders).


# 3. alias/orders, rotation on.


# 4. Grant reporting-read: reporting may Decrypt, context app=orders.


# 5. A data key (AES_256, context app=orders); save the encrypted copy to
#    orders.key.enc as raw bytes.


# 6. A multi-Region key "orders global" with the same policy,
#    alias/orders-global, replicated to eu-west-1.

