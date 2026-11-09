---
title: Events and workflows
summary: A Step Functions state machine with retries, a catch and a choice - written in Amazon States Language - started every night by an EventBridge schedule.
order: 4
files: [setup.sh, workflow.json]
run: awslab run setup.sh
hints:
  - "A Task state calls a Lambda function by ARN: `\"Resource\": \"arn:aws:lambda:us-east-1:123456789012:function:charge\"`. Retry is a list: `[{\"ErrorEquals\": [\"States.TaskFailed\"], \"IntervalSeconds\": 2, \"MaxAttempts\": 3, \"BackoffRate\": 2}]`."
  - "Catch sends errors elsewhere: `\"Catch\": [{\"ErrorEquals\": [\"States.ALL\"], \"Next\": \"Failed\"}]`. A Choice state: `\"Choices\": [{\"Variable\": \"$.paid\", \"BooleanEquals\": true, \"Next\": \"Ship\"}], \"Default\": \"Failed\"`."
  - "`aws stepfunctions create-state-machine --name order-flow --definition file://workflow.json --role-arn \"$SFN_ROLE\" --query stateMachineArn --output text`."
  - "`aws events put-rule --name nightly-orders --schedule-expression 'cron(0 2 * * ? *)'`, then `aws events put-targets --rule nightly-orders --targets \"Id=order-flow,Arn=$SM_ARN,RoleArn=$EVENTS_ROLE\"`."
---

Some work is a sequence: charge the card, then - if that worked - ship,
and if anything failed, tell someone. Writing that as code means handling
retries, timeouts, waits and partial failure yourself. **Step Functions**
does it as a **state machine**, defined in JSON (**Amazon States
Language**), with every execution's history visible step by step.

## States

| Type | Does |
|---|---|
| `Task` | calls a service: a Lambda function, or 200+ AWS APIs directly (DynamoDB, SQS, ECS...) |
| `Choice` | branches on the data |
| `Parallel`, `Map` | branches at once; one branch per item |
| `Wait` | waits a time, or until a timestamp |
| `Pass`, `Succeed`, `Fail` | moves data on; ends the run |

Every Task can **Retry** (which errors, how many times, with what backoff)
and **Catch** (where to go when retries run out). That is most of the error
handling an application needs, without writing any.

**Standard** workflows run up to a year with exactly-once steps;
**Express** workflows are cheaper and faster for high-volume, short runs.

## Starting it on a schedule

**EventBridge** rules match events - or run on a **schedule** - and send
them to targets: Lambda, a state machine, a queue... For a state machine
the rule needs a **role** allowing `states:StartExecution`. Cron expressions
in EventBridge have six fields and are in UTC: `cron(0 2 * * ? *)` is 02:00
every day. (**EventBridge Scheduler** is the newer service for one-off and
recurring schedules at scale.)

## Your task

The script creates the roles (one for the state machine, one for
EventBridge). Write **`workflow.json`** with these states, starting at
**Charge**:

- **Charge**: a Task calling the Lambda function `charge`, retrying
  `States.TaskFailed` **3** times with backoff **2**, catching **States.ALL**
  to **Failed**, then going to **CheckPaid**;
- **CheckPaid**: a Choice - if `$.paid` is true, go to **Ship**; otherwise
  **Failed**;
- **Ship**: a Task calling the function `ship`, ending the run;
- **Failed**: a Fail state.

Then create the state machine **`order-flow`** from it, and an EventBridge
rule **`nightly-orders`** at **02:00 UTC every day** targeting it with the
EventBridge role.
