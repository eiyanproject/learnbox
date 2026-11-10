#!/usr/bin/env bash
# CI/CD 1: CodeBuild and CodePipeline.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# Done for you: the build's secret and the application.
SECRET_ARN=$(aws secretsmanager create-secret --name ci/sonar-token \
  --secret-string not-a-real-token --query ARN --output text)
printf 'def total(items):\n    return sum(i["price"] * i["qty"] for i in items)\n' > app.py
printf 'from app import total\n\n\ndef test_total():\n    assert total([{"price": 2, "qty": 3}]) == 6\n' > test_app.py
printf 'Resources:\n  Orders:\n    Type: AWS::SQS::Queue\n    Properties:\n      QueueName: orders\n' > template.yaml

# 1. buildspec.yml (edit the file).

trust() {
  echo "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"$1\"},\"Action\":\"sts:AssumeRole\"}]}"
}
BUCKET=lb-pipeline-artifacts

# 2. Key alias/pipeline; bucket lb-pipeline-artifacts, versioned, SSE-KMS.
KEY_ID=$(aws kms create-key --description "pipeline artifacts" --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/pipeline --target-key-id "$KEY_ID"
KEY_ARN=$(aws kms describe-key --key-id "$KEY_ID" --query KeyMetadata.Arn --output text)
aws s3api create-bucket --bucket "$BUCKET" >/dev/null
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  "{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\",\"KMSMasterKeyID\":\"$KEY_ARN\"},\"BucketKeyEnabled\":true}]}"

# 3. Zip the four files to s3://lb-pipeline-artifacts/source/orders-api.zip.
python3 -c "
import zipfile
with zipfile.ZipFile('orders-api.zip', 'w') as z:
    for f in ['buildspec.yml', 'app.py', 'test_app.py', 'template.yaml']:
        z.write(f)
"
aws s3api put-object --bucket "$BUCKET" --key source/orders-api.zip --body orders-api.zip >/dev/null

# 4. Role codebuild-orders-api with its inline policy.
BUILD_ROLE=$(aws iam create-role --role-name codebuild-orders-api \
  --assume-role-policy-document "$(trust codebuild.amazonaws.com)" --query Role.Arn --output text)
cat > build-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
     "Resource": "arn:aws:logs:us-east-1:$ACCOUNT:log-group:/aws/codebuild/orders-api-build*"},
    {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"],
     "Resource": "arn:aws:s3:::$BUCKET/*"},
    {"Effect": "Allow", "Action": "secretsmanager:GetSecretValue", "Resource": "$SECRET_ARN"},
    {"Effect": "Allow", "Action": ["kms:Decrypt", "kms:GenerateDataKey"], "Resource": "$KEY_ARN"}
  ]
}
EOF
aws iam put-role-policy --role-name codebuild-orders-api --policy-name build \
  --policy-document file://build-policy.json

# 5. Project orders-api-build.
aws codebuild create-project --name orders-api-build \
  --source "type=S3,location=$BUCKET/source/orders-api.zip" \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL \
  --service-role "$BUILD_ROLE" --timeout-in-minutes 20 >/dev/null

# 6. Roles codepipeline-orders-api and cfn-deploy (AmazonSQSFullAccess).
PIPE_ROLE=$(aws iam create-role --role-name codepipeline-orders-api \
  --assume-role-policy-document "$(trust codepipeline.amazonaws.com)" --query Role.Arn --output text)
CFN_ROLE=$(aws iam create-role --role-name cfn-deploy \
  --assume-role-policy-document "$(trust cloudformation.amazonaws.com)" --query Role.Arn --output text)
aws iam attach-role-policy --role-name cfn-deploy --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess

# 7. Pipeline orders-api: Source, Build, Approve, Deploy.
python3 - "$PIPE_ROLE" "$BUCKET" "$KEY_ARN" "$CFN_ROLE" > pipeline.json <<'PY'
import json, sys
role, bucket, key, cfn = sys.argv[1:]
def action(name, category, provider, configuration, inputs=(), outputs=()):
    return {"name": name,
            "actionTypeId": {"category": category, "owner": "AWS", "provider": provider, "version": "1"},
            "configuration": configuration,
            "inputArtifacts": [{"name": n} for n in inputs],
            "outputArtifacts": [{"name": n} for n in outputs]}
print(json.dumps({"pipeline": {
    "name": "orders-api",
    "roleArn": role,
    "artifactStore": {"type": "S3", "location": bucket,
                      "encryptionKey": {"id": key, "type": "KMS"}},
    "stages": [
        {"name": "Source", "actions": [action("Source", "Source", "S3", {
            "S3Bucket": bucket, "S3ObjectKey": "source/orders-api.zip",
            "PollForSourceChanges": "false"}, outputs=["SourceOutput"])]},
        {"name": "Build", "actions": [action("Build", "Build", "CodeBuild", {
            "ProjectName": "orders-api-build"}, inputs=["SourceOutput"], outputs=["BuildOutput"])]},
        {"name": "Approve", "actions": [action("Approve", "Approval", "Manual", {
            "CustomData": "Check the test report before deploying."})]},
        {"name": "Deploy", "actions": [action("Deploy", "Deploy", "CloudFormation", {
            "ActionMode": "CREATE_UPDATE", "StackName": "orders-api",
            "TemplatePath": "BuildOutput::template.yaml", "RoleArn": cfn},
            inputs=["BuildOutput"])]},
    ],
}}, indent=2))
PY
aws codepipeline create-pipeline --cli-input-json file://pipeline.json >/dev/null
PIPELINE_ARN="arn:aws:codepipeline:us-east-1:$ACCOUNT:orders-api"

# 8. EventBridge: bucket notifications, role events-orders-api, rule
#    orders-api-source targeting the pipeline.
aws s3api put-bucket-notification-configuration --bucket "$BUCKET" \
  --notification-configuration '{"EventBridgeConfiguration": {}}'
EVENTS_ROLE=$(aws iam create-role --role-name events-orders-api \
  --assume-role-policy-document "$(trust events.amazonaws.com)" --query Role.Arn --output text)
aws iam put-role-policy --role-name events-orders-api --policy-name start-pipeline \
  --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"codepipeline:StartPipelineExecution\",\"Resource\":\"$PIPELINE_ARN\"}]}"
aws events put-rule --name orders-api-source --event-pattern "{
  \"source\": [\"aws.s3\"],
  \"detail-type\": [\"Object Created\"],
  \"detail\": {\"bucket\": {\"name\": [\"$BUCKET\"]}, \"object\": {\"key\": [\"source/orders-api.zip\"]}}
}" >/dev/null
aws events put-targets --rule orders-api-source \
  --targets "Id=pipeline,Arn=$PIPELINE_ARN,RoleArn=$EVENTS_ROLE" >/dev/null
