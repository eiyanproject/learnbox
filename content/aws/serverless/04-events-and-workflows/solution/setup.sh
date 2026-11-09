#!/usr/bin/env bash
# Serverless 4: events and workflows.
set -euo pipefail

# Done for you: a role the state machine runs as, and one EventBridge uses
# to start it.
trust() { echo "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"$1\"},\"Action\":\"sts:AssumeRole\"}]}"; }
SFN_ROLE=$(aws iam create-role --role-name order-flow --assume-role-policy-document \
  "$(trust states.amazonaws.com)" --query Role.Arn --output text)
EVENTS_ROLE=$(aws iam create-role --role-name nightly-orders --assume-role-policy-document \
  "$(trust events.amazonaws.com)" --query Role.Arn --output text)

# 1. workflow.json (edit the file).

# 2. The state machine order-flow from it, running as SFN_ROLE.
SM_ARN=$(aws stepfunctions create-state-machine --name order-flow \
  --definition file://workflow.json --role-arn "$SFN_ROLE" \
  --query stateMachineArn --output text)

# 3. The EventBridge rule nightly-orders, 02:00 UTC daily, targeting order-flow
#    with EVENTS_ROLE.
aws events put-rule --name nightly-orders \
  --schedule-expression 'cron(0 2 * * ? *)' --query RuleArn --output text
aws events put-targets --rule nightly-orders \
  --targets "Id=order-flow,Arn=$SM_ARN,RoleArn=$EVENTS_ROLE" >/dev/null
