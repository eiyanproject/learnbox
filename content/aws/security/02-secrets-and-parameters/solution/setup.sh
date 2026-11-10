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
PASSWORD=$(aws secretsmanager get-random-password --password-length 32 \
  --exclude-punctuation --query RandomPassword --output text)
python3 -c 'import json, sys; print(json.dumps({"username": "orders", "password": sys.argv[1]}))' \
  "$PASSWORD" > db-secret.json
SECRET_ARN=$(aws secretsmanager create-secret --name prod/orders/db \
  --kms-key-id alias/app --secret-string file://db-secret.json \
  --tags Key=env,Value=prod --query ARN --output text)
rm db-secret.json

# 2. Rotate every 30 days with rotate-db, not immediately.
aws secretsmanager rotate-secret --secret-id prod/orders/db \
  --rotation-lambda-arn "$ROTATE_ARN" \
  --rotation-rules AutomaticallyAfterDays=30 --no-rotate-immediately >/dev/null

# 3. The role orders-app (trusted by ecs-tasks.amazonaws.com), and a resource
#    policy on the secret denying GetSecretValue to everyone else.
APP_ARN=$(aws iam create-role --role-name orders-app \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query Role.Arn --output text)
cat > secret-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "OnlyOrdersApp",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "*",
    "Condition": {"StringNotEquals": {"aws:PrincipalArn": "$APP_ARN"}}
  }]
}
EOF
aws secretsmanager put-resource-policy --secret-id prod/orders/db \
  --resource-policy file://secret-policy.json >/dev/null

# 4. /orders/prod/db_host (String), /orders/prod/allowed_origins
#    (StringList), /orders/prod/api_key (SecureString, alias/app).
aws ssm put-parameter --name /orders/prod/db_host --type String \
  --value orders.db.internal >/dev/null
aws ssm put-parameter --name /orders/prod/allowed_origins --type StringList \
  --value "https://shop.example.com,https://admin.example.com" >/dev/null
aws ssm put-parameter --name /orders/prod/api_key --type SecureString \
  --key-id alias/app --value "$(openssl rand -hex 16 2>/dev/null || echo k-$RANDOM$RANDOM)" >/dev/null

# 5. Inline policy read-config on orders-app: the /orders/prod branch, the
#    secret, and kms:Decrypt on the key.
cat > read-config.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {"Sid": "Parameters", "Effect": "Allow",
     "Action": ["ssm:GetParametersByPath", "ssm:GetParameters"],
     "Resource": ["arn:aws:ssm:us-east-1:$ACCOUNT:parameter/orders/prod",
                  "arn:aws:ssm:us-east-1:$ACCOUNT:parameter/orders/prod/*"]},
    {"Sid": "Secret", "Effect": "Allow",
     "Action": "secretsmanager:GetSecretValue", "Resource": "$SECRET_ARN"},
    {"Sid": "Decrypt", "Effect": "Allow",
     "Action": "kms:Decrypt", "Resource": "$KEY_ARN"}
  ]
}
EOF
aws iam put-role-policy --role-name orders-app --policy-name read-config \
  --policy-document file://read-config.json
