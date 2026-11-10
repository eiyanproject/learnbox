#!/usr/bin/env bash
# Security 1: KMS key policies and envelope encryption.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# 1. Roles orders-app and reporting (trusted by ec2.amazonaws.com) and
#    key-admin (trusted by the account).
EC2_TRUST='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
APP_ARN=$(aws iam create-role --role-name orders-app \
  --assume-role-policy-document "$EC2_TRUST" --query Role.Arn --output text)
REPORTING_ARN=$(aws iam create-role --role-name reporting \
  --assume-role-policy-document "$EC2_TRUST" --query Role.Arn --output text)
ADMIN_ARN=$(aws iam create-role --role-name key-admin \
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::$ACCOUNT:root\"},\"Action\":\"sts:AssumeRole\"}]}" \
  --query Role.Arn --output text)

# 2. A key "orders data" with a three-statement key policy.
python3 - "$ACCOUNT" "$ADMIN_ARN" "$APP_ARN" > key-policy.json <<'PY'
import json, sys
account, admin, app = sys.argv[1:]
print(json.dumps({"Version": "2012-10-17", "Statement": [
    {"Sid": "EnableIAM", "Effect": "Allow",
     "Principal": {"AWS": f"arn:aws:iam::{account}:root"},
     "Action": "kms:*", "Resource": "*"},
    {"Sid": "KeyAdministrators", "Effect": "Allow",
     "Principal": {"AWS": admin},
     "Action": ["kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*",
                "kms:Put*", "kms:Update*", "kms:Revoke*", "kms:Disable*",
                "kms:Get*", "kms:Delete*", "kms:TagResource", "kms:UntagResource",
                "kms:ScheduleKeyDeletion", "kms:CancelKeyDeletion"],
     "Resource": "*"},
    {"Sid": "OrdersAppUse", "Effect": "Allow",
     "Principal": {"AWS": app},
     "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey*", "kms:DescribeKey"],
     "Resource": "*",
     "Condition": {"StringEquals": {"kms:EncryptionContext:app": "orders"}}},
]}, indent=2))
PY
KEY_ID=$(aws kms create-key --description "orders data" \
  --policy file://key-policy.json --query KeyMetadata.KeyId --output text)

# 3. alias/orders, rotation on.
aws kms create-alias --alias-name alias/orders --target-key-id "$KEY_ID"
aws kms enable-key-rotation --key-id "$KEY_ID"

# 4. Grant reporting-read: reporting may Decrypt, context app=orders.
aws kms create-grant --key-id "$KEY_ID" --name reporting-read \
  --grantee-principal "$REPORTING_ARN" --operations Decrypt \
  --constraints EncryptionContextSubset={app=orders} >/dev/null

# 5. A data key (AES_256, context app=orders); keep only the encrypted copy.
aws kms generate-data-key --key-id alias/orders --key-spec AES_256 \
  --encryption-context app=orders \
  --query CiphertextBlob --output text | base64 -d > orders.key.enc

# 6. A multi-Region key "orders global" with the same policy,
#    alias/orders-global, replicated to eu-west-1.
GLOBAL_ID=$(aws kms create-key --multi-region --description "orders global" \
  --policy file://key-policy.json --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/orders-global --target-key-id "$GLOBAL_ID"
aws kms replicate-key --key-id "$GLOBAL_ID" --replica-region eu-west-1 >/dev/null
