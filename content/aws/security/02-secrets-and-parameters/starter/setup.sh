#!/usr/bin/env bash
# Security 2: Secrets Manager and Parameter Store.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# Done for you: the key alias/app and the rotation function rotate-db.
KEY_ID=$(aws kms create-key --description "app secrets" --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/app --target-key-id "$KEY_ID"
KEY_ARN=$(aws kms describe-key --key-id "$KEY_ID" --query KeyMetadata.Arn --output text)
aws iam create-role --role-name rotate-db \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
printf 'def handler(event, context):\n    """createSecret, setSecret, testSecret, finishSecret."""\n' > rotate.py
python3 -c "import zipfile; zipfile.ZipFile('rotate.zip', 'w').write('rotate.py')"
ROTATE_ARN=$(aws lambda create-function --function-name rotate-db --runtime python3.12 \
  --handler rotate.handler --role "arn:aws:iam::$ACCOUNT:role/rotate-db" \
  --zip-file fileb://rotate.zip --query FunctionArn --output text)

# 1. The secret prod/orders/db: alias/app, tag env=prod, JSON with username
#    orders and a generated 32-character password without punctuation.


# 2. Rotate every 30 days with rotate-db, not immediately.


# 3. The role orders-app (trusted by ecs-tasks.amazonaws.com), and a resource
#    policy on the secret denying GetSecretValue to everyone else.


# 4. /orders/prod/db_host (String), /orders/prod/allowed_origins
#    (StringList), /orders/prod/api_key (SecureString, alias/app).


# 5. Inline policy read-config on orders-app: the /orders/prod branch, the
#    secret, and kms:Decrypt on the key.

