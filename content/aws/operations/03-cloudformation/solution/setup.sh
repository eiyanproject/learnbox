#!/usr/bin/env bash
# Operations 3: infrastructure as code with CloudFormation.
set -euo pipefail

# 1. template.yaml (edit the file).

# 2. Deploy it as app-dev: Env=dev, stack tag env=dev, termination protection,
#    and wait for it to finish.
aws cloudformation create-stack --stack-name app-dev \
  --template-body file://template.yaml \
  --parameters ParameterKey=Env,ParameterValue=dev \
  --tags Key=env,Value=dev \
  --enable-termination-protection \
  --query StackId --output text
aws cloudformation wait stack-create-complete --stack-name app-dev
aws cloudformation describe-stacks --stack-name app-dev \
  --query 'Stacks[0].Outputs' --output table
