#!/usr/bin/env bash
# CI/CD 2: Lambda canaries with CodeDeploy.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# Done for you: the function's role, both versions' code, the smoke test.
aws iam create-role --role-name orders-api-fn \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
FN_ROLE="arn:aws:iam::$ACCOUNT:role/orders-api-fn"
for v in 1 2; do
  printf 'def handler(event, context):\n    return {"version": %s}\n' "$v" > handler.py
  python3 -c "import zipfile; zipfile.ZipFile('v$v.zip', 'w').write('handler.py')"
done
printf 'def handler(event, context):\n    """Call the new version, then report to CodeDeploy."""\n' > smoke.py
python3 -c "import zipfile; zipfile.ZipFile('smoke.zip', 'w').write('smoke.py')"
aws lambda create-function --function-name orders-api-smoke --runtime python3.12 \
  --handler smoke.handler --role "$FN_ROLE" --zip-file fileb://smoke.zip >/dev/null

# 1. orders-api from v1.zip, published as version 1.


# 2. Alias live -> 1.


# 3. v2.zip, published as version 2.


# 4. Alarm orders-api-errors on the live alias.


# 5. Role codedeploy-orders-api (AWSCodeDeployRoleForLambda).


# 6. Application orders-api (Lambda) and deployment group live.


# 7. appspec.yml (edit the file).
