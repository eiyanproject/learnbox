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
aws lambda create-function --function-name orders-api --runtime python3.12 \
  --handler handler.handler --role "$FN_ROLE" --zip-file fileb://v1.zip --publish >/dev/null

# 2. Alias live -> 1.
aws lambda create-alias --function-name orders-api --name live --function-version 1 >/dev/null

# 3. v2.zip, published as version 2.
aws lambda update-function-code --function-name orders-api --zip-file fileb://v2.zip >/dev/null
aws lambda publish-version --function-name orders-api --description "release 2" >/dev/null

# 4. Alarm orders-api-errors on the live alias.
aws cloudwatch put-metric-alarm --alarm-name orders-api-errors \
  --namespace AWS/Lambda --metric-name Errors \
  --dimensions Name=FunctionName,Value=orders-api Name=Resource,Value=orders-api:live \
  --statistic Sum --period 60 --evaluation-periods 1 --threshold 0 \
  --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching

# 5. Role codedeploy-orders-api (AWSCodeDeployRoleForLambda).
DEPLOY_ROLE=$(aws iam create-role --role-name codedeploy-orders-api \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"codedeploy.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query Role.Arn --output text)
aws iam attach-role-policy --role-name codedeploy-orders-api \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForLambda

# 6. Application orders-api (Lambda) and deployment group live.
aws deploy create-application --application-name orders-api --compute-platform Lambda >/dev/null
aws deploy create-deployment-group --application-name orders-api \
  --deployment-group-name live --service-role-arn "$DEPLOY_ROLE" \
  --deployment-config-name CodeDeployDefault.LambdaCanary10Percent5Minutes \
  --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL \
  --auto-rollback-configuration enabled=true,events=DEPLOYMENT_FAILURE,DEPLOYMENT_STOP_ON_ALARM \
  --alarm-configuration 'enabled=true,alarms=[{name=orders-api-errors}]' >/dev/null

# 7. appspec.yml (edit the file).
