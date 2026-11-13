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

Some work is a **sequence** with rules: charge the card; if that worked,
ship the order; if anything failed, stop and record it; and if the card
company's service hiccups, try again a few times before giving up. Written
as ordinary code in one function, that means handling retries, waiting,
timeouts and half-finished runs yourself, and when something goes wrong at
2 a.m., working out from logs which step it reached.

**Step Functions** runs such a sequence as a **state machine**: a set of
named **states** (steps) and the transitions between them, written in JSON
in a language called **Amazon States Language** (ASL). Step Functions keeps
track of where each run (an **execution**) is, retries and catches errors as
the definition says, and shows every execution's history step by step. This
lesson's workflow, and the schedule that starts it:

```text
 EventBridge rule nightly-orders, cron(0 2 * * ? *)  ──starts──>  state machine order-flow

   Charge (Task: Lambda charge) ──ok──> CheckPaid (Choice) ──$.paid is true──> Ship (Task: Lambda ship) ──> end
      │ retries TaskFailed 3x, backoff 2         │
      │ any error left: catch                    └── otherwise ──┐
      └──────────────────────────────────────────────────────────┴──> Failed (Fail)
```

## States

| Type | Does |
|---|---|
| `Task` | does one piece of work: calls a Lambda function, or one of 200+ AWS APIs directly (DynamoDB, SQS, ECS...) |
| `Choice` | branches on the data: "if `paid` is true, go to Ship" |
| `Parallel`, `Map` | runs branches at the same time; one branch per item of a list |
| `Wait` | waits a number of seconds, or until a timestamp |
| `Pass` | passes its input on, possibly changed |
| `Succeed`, `Fail` | end the execution, successfully or not |

A definition names the first state in `StartAt`, and lists every state
under `States`, each with a `Type`. Every state except a final one says
where to go next, with `"Next": "<state name>"`; a final Task or Pass says
`"End": true` instead. For example, a two-step workflow that waits and then
calls a function:

```json
{
  "StartAt": "Pause",
  "States": {
    "Pause":  { "Type": "Wait", "Seconds": 60, "Next": "Notify" },
    "Notify": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123456789012:function:notify", "End": true }
  }
}
```

A Task's `Resource` for a Lambda function is the function's ARN.

## Data, and Choice

An execution starts with a JSON **input**, and each state passes its output
to the next. A Lambda Task's output is what the function returned, so if
`charge` returns `{"paid": true}`, the next state sees that. A Choice state
reads it with a **path**: `$.paid` means "the field `paid` of the current
data" (`$` is the whole document):

```json
"CheckStock": {
  "Type": "Choice",
  "Choices": [{ "Variable": "$.inStock", "BooleanEquals": true, "Next": "Reserve" }],
  "Default": "OutOfStock"
}
```

The rules are tried in order; `Default` is where to go when none matches.
Other comparisons include `StringEquals`, `NumericGreaterThan` and
`IsPresent`.

## Retry and Catch

Any Task can **Retry** and **Catch**, which is most of the error handling a
workflow needs, without writing any:

```json
"Retry": [{
  "ErrorEquals": ["States.TaskFailed"],
  "IntervalSeconds": 2, "MaxAttempts": 3, "BackoffRate": 2
}],
"Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "Failed" }]
```

- **Retry** says which errors to retry and how: wait `IntervalSeconds`
  before the first retry, multiply the wait by `BackoffRate` each time (2,
  then 4, then 8 seconds: **exponential backoff**, which gives a struggling
  service room to recover), and give up after `MaxAttempts` retries.
- **Catch** says where to go when an error is not retried, or the retries
  run out. Without it, the execution fails at that state.
- `States.TaskFailed` matches any failure of the task except a timeout
  (`States.Timeout`); `States.ALL` matches every error, and must be alone
  in its `ErrorEquals` and come last.
- Retries happen first; a Catch only takes over when retrying is over. Left
  out, `IntervalSeconds` defaults to 1, `MaxAttempts` to 3 and
  `BackoffRate` to 2.0.
- Only states that do work (Task, Parallel, Map) can Retry and Catch;
  Choice, Wait, Pass, Succeed and Fail cannot.

## Standard or Express

**Standard** workflows can run for up to a year, run each step exactly
once, and keep a full history: right for business processes like this one.
**Express** workflows run for at most five minutes and are much cheaper per
execution: right for high-volume, short jobs such as processing streaming
events.

## Starting it on a schedule

**EventBridge** routes events to **targets**. A **rule** either matches
events (from your applications, or from AWS services, such as "an EC2
instance stopped") or runs on a **schedule**. Its targets can be a Lambda
function, a queue, a state machine, and many more.

To start a state machine, EventBridge needs permission to call
`states:StartExecution`, so the target is given a **role** for EventBridge
(`events.amazonaws.com`) to assume. The starter creates both roles for you:
`order-flow` for the state machine itself (in `SFN_ROLE`) and
`nightly-orders` for EventBridge (in `EVENTS_ROLE`).

EventBridge's cron expressions have **six** fields, one more than
Auto Scaling's (Compute lesson 3), and are in UTC:

```text
 cron( minute  hour  day-of-month  month  day-of-week  year )
 cron(   0      2         *          *         ?         *  )   = 02:00 UTC every day
```

One of day-of-month and day-of-week **must** be `?` ("no particular
value"), since saying both could contradict itself; real EventBridge refuses
`cron(0 2 * * * *)` as not valid (the emulator does not check). For a simple
interval, `rate(5 minutes)` works too. (**EventBridge Scheduler** is a newer,
separate service for one-off and recurring schedules at large scale, with
time zones and retries, and AWS now recommends it over scheduled rules for
new work; scheduled rules, used here, still work the same.)

A rule's target is given as `Id=...,Arn=...,RoleArn=...`, where the `Id` is
any name you choose for that target within the rule.

## Where Step Functions fits

Step Functions **orchestrates**: one place holds the order of the steps,
their retries and their branches, and each step stays a small function or
service call. That is the opposite of **choreography** with events (lesson
2's fan-out), where each service reacts on its own and nobody holds the
whole picture. Workflows with a **human approval** use a task that pauses
until a token is sent back (`.waitForTaskToken`), up to a year for Standard
workflows.

## Your task

The script creates the two roles. Write **`workflow.json`** (it starts with
`StartAt` set to `Charge` and no states) with four states:

- **Charge**: a **Task** calling the Lambda function `charge`
  (`arn:aws:lambda:us-east-1:123456789012:function:charge`); retrying
  **`States.TaskFailed`** with **`MaxAttempts` 3** and **`BackoffRate` 2**;
  catching **`States.ALL`** to go to **Failed**; and otherwise going on to
  **CheckPaid**;
- **CheckPaid**: a **Choice**: if `$.paid` is `true`, go to **Ship**;
  otherwise (`Default`) to **Failed**;
- **Ship**: a **Task** calling the function `ship`, ending the run
  (`"End": true`);
- **Failed**: a **Fail** state.

Then create the state machine **`order-flow`** from it, running as
`SFN_ROLE`, and an EventBridge rule **`nightly-orders`** that runs at
**02:00 UTC every day**, targeting the state machine (by its ARN) with
`EVENTS_ROLE`.

After **Run**, `aws stepfunctions describe-state-machine --state-machine-arn
"<the ARN>" --query definition --output text` prints your definition as
stored, and `aws events list-targets-by-rule --rule nightly-orders` the
target. (The functions `charge` and `ship` do not exist here, and nothing
runs at 02:00; the emulator only keeps the definitions.)

## Check yourself

1. Charge fails three times in a row. What happens?
   *Retries are exhausted, the Catch sends the execution to Failed.*
2. Where does `$.paid` come from?
   *From the output of the previous state, the charge function's result.*
3. Why is `cron(0 2 * * * *)` invalid in EventBridge?
   *One of day-of-month and day-of-week must be `?`.*
4. Why does the EventBridge rule need a role?
   *To call `states:StartExecution` on the state machine.*
