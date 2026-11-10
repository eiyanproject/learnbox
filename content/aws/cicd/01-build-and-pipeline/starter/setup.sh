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

# 2. Key alias/pipeline; bucket lb-pipeline-artifacts, versioned, SSE-KMS.


# 3. Zip buildspec.yml app.py test_app.py template.yaml to
#    s3://lb-pipeline-artifacts/source/orders-api.zip.


# 4. Role codebuild-orders-api with its inline policy.


# 5. Project orders-api-build.


# 6. Roles codepipeline-orders-api and cfn-deploy (AmazonSQSFullAccess).


# 7. Pipeline orders-api: Source, Build, Approve, Deploy.


# 8. EventBridge: bucket notifications, role events-orders-api, rule
#    orders-api-source targeting the pipeline.

