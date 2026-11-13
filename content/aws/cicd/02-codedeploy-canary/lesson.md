---
title: Lambda canaries with CodeDeploy
summary: Two published versions behind an alias, an error alarm on the alias, a CodeDeploy deployment group that shifts 10% of traffic for five minutes and rolls back on that alarm, and the AppSpec that describes the release - with a pre-traffic test hook.
order: 2
files: [setup.sh, appspec.yml]
run: awslab run setup.sh
hints:
  - "`aws lambda create-function ... --publish` makes version 1 at once. After `aws lambda update-function-code --function-name orders-api --zip-file fileb://v2.zip`, `aws lambda publish-version --function-name orders-api` makes version 2."
  - "`aws lambda create-alias --function-name orders-api --name live --function-version 1`."
  - "`aws cloudwatch put-metric-alarm --alarm-name orders-api-errors --namespace AWS/Lambda --metric-name Errors --dimensions Name=FunctionName,Value=orders-api Name=Resource,Value=orders-api:live --statistic Sum --period 60 --evaluation-periods 1 --threshold 0 --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching`."
  - "`aws deploy create-deployment-group --application-name orders-api --deployment-group-name live --service-role-arn \"$DEPLOY_ROLE\" --deployment-config-name CodeDeployDefault.LambdaCanary10Percent5Minutes --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL --auto-rollback-configuration enabled=true,events=DEPLOYMENT_FAILURE,DEPLOYMENT_STOP_ON_ALARM --alarm-configuration enabled=true,alarms=[{name=orders-api-errors}]`."
  - "appspec.yml: `version: 0.0`, then `Resources:` with one item `- orders-api:` holding `Type: AWS::Lambda::Function` and `Properties: {Name, Alias, CurrentVersion, TargetVersion}`, then `Hooks:` with `- BeforeAllowTraffic: orders-api-smoke`. Quote the versions: `\"1\"`."
---

The previous lesson's pipeline replaced the old version with the new one in
one step. If the new version has a bug, **every** user meets it at once.
A **canary** deployment avoids that: first send a small share of traffic,
say 10%, to the new version, watch for errors, and only then send the rest,
or, if errors appear, go back by itself. (The name comes from the canaries
miners carried to warn them of gas.) **CodeDeploy** runs canaries for
Lambda functions, ECS services and EC2 fleets. This lesson sets one up for
a Lambda function.

```text
 callers ──> alias orders-api:live
               before:  100% version 1
               hook:    orders-api-smoke tests version 2 (gets no traffic yet)
               step 1:   90% version 1 / 10% version 2   for 5 minutes, alarm orders-api-errors watching
               step 2:  100% version 2                    (or, if the alarm fires: back to 100% version 1)
```

## Versions and aliases

A Lambda function's code and settings can change at any time; the editable
copy is called **`$LATEST`**. To deploy safely you need fixed points:

- **`publish-version`** freezes the current code and configuration as an
  **immutable, numbered version** (1, 2, 3...). `create-function
  --publish` makes version 1 at once.
- An **alias** (`live`) is a named **pointer** to a version, with its own
  ARN (`...:function:orders-api:live`). Callers, API Gateway and event
  sources use the alias, never `$LATEST` and never a bare version number,
  so a release moves one pointer instead of reconfiguring every caller.
- An alias can **split traffic** between two versions with weights (its
  `RoutingConfig`), and that is what CodeDeploy changes step by step.

```
$ aws lambda list-versions-by-function --function-name orders-api --query 'Versions[].Version' --output text
$LATEST	1	2
$ aws lambda get-alias --function-name orders-api --name live --query '[FunctionVersion,RoutingConfig]'
[
    "1",
    null
]
```

`RoutingConfig` is `null` until a deployment adds weights.

## Deployment configurations

A deployment configuration says how traffic moves. The predefined ones for
Lambda:

| Configuration | What happens | Total time |
|---|---|---|
| `CodeDeployDefault.LambdaCanary10Percent5Minutes` | 10% to the new version, then **all** of it after 5 minutes | 5 min |
| `...LambdaCanary10Percent10Minutes`, `15Minutes`, `30Minutes` | the same, with a longer wait | 10-30 min |
| `...LambdaLinear10PercentEvery1Minute` (also 2, 3, 10 minutes) | +10% every minute, in ten equal steps | 10 min |
| `...LambdaAllAtOnce` | everything at once, still with hooks and rollback | at once |

**Canary** is two steps; **linear** is many equal steps. The exam's words:
"a small share first, then everything" is canary; "gradually, in equal
increments" is linear.

For Lambda, a deployment group always uses the deployment type
**`BLUE_GREEN`** with **`WITH_TRAFFIC_CONTROL`**: version 1 is "blue",
version 2 "green", and CodeDeploy controls the alias's traffic between
them. The **CodeDeploy service role** (trusted by
`codedeploy.amazonaws.com`, with the managed
`service-role/AWSCodeDeployRoleForLambda`) lets CodeDeploy update the
alias, read alarms and invoke hooks.

## The AppSpec

The **AppSpec** file describes one release: which function and alias,
from which version to which, and the **hooks** to run. For Lambda its
`version` is always `0.0`:

```yaml
version: 0.0
Resources:
  - orders-api:                     # any name for this resource
      Type: AWS::Lambda::Function
      Properties:
        Name: orders-api
        Alias: live
        CurrentVersion: "1"         # quoted: versions are strings
        TargetVersion: "2"
Hooks:
  - BeforeAllowTraffic: orders-api-smoke
```

A deployment is then started with `aws deploy create-deployment`, passing
this AppSpec.

## Hooks: testing before users see it

Lambda deployments have two hooks, each a Lambda function CodeDeploy
invokes:

| Hook | Runs | Typical job |
|---|---|---|
| **`BeforeAllowTraffic`** | before the alias sends **any** traffic to the new version | call version 2 directly with test requests |
| **`AfterAllowTraffic`** | after all traffic has moved | end-to-end checks through the alias |

The hook function must report its result by calling
**`codedeploy:PutLifecycleEventHookExecutionStatus`** with `Succeeded` or
`Failed`, passing the deployment ID and hook execution ID it was invoked
with. If it reports `Failed`, or never reports (within an hour), the
deployment fails and rolls back. So the hook's own role needs that
permission, plus `lambda:InvokeFunction` on what it tests.

❗ In real AWS, `AWSCodeDeployRoleForLambda` lets CodeDeploy invoke only
functions whose names start with **`CodeDeployHook_`**:

```json
{"Action": ["lambda:InvokeFunction"], "Effect": "Allow",
 "Resource": "arn:aws:lambda:*:*:function:CodeDeployHook_*"}
```

The emulator does not check this, so this lesson's hook keeps the name
`orders-api-smoke`. In a real account, either name the hook function
`CodeDeployHook_orders-api-smoke`, or add an inline policy to the
CodeDeploy role allowing `lambda:InvokeFunction` on the hook's ARN.
Otherwise the deployment fails at `BeforeAllowTraffic`, before any traffic
moves.

## Rollback on an alarm

**Automatic rollback** returns the alias to 100% of the old version when:

- `DEPLOYMENT_FAILURE`: the deployment fails, a hook failing included;
- `DEPLOYMENT_STOP_ON_ALARM`: one of the **alarms** attached to the
  deployment group goes into `ALARM` while the deployment runs.

This lesson's alarm fires on **any** error of the `live` alias:

| Setting | Value | Why |
|---|---|---|
| Metric | `AWS/Lambda` `Errors` | invocations that ended in an error |
| Dimensions | `FunctionName=orders-api`, `Resource=orders-api:live` | the alias's metric, not the whole function's |
| Statistic, period | `Sum` over 60 s, for 1 period | react within a minute |
| Threshold | `> 0` | any error at all |
| Missing data | `notBreaching` | a minute with no calls is not an error |

During the five-minute canary only 10% of calls reach version 2, so a
version that fails even sometimes shows up in that window, and only a tenth
of users meet it. That turns "watch the graphs after a deploy" into
something the system does.

The same model deploys **ECS** services (with a test listener on the load
balancer) and **EC2** fleets (with lifecycle scripts in the AppSpec): see
the DOP practice questions.

## Your task

Done for you: the role `orders-api-fn`, the code of both versions
(`v1.zip`, `v2.zip`), and the smoke-test function **`orders-api-smoke`**.

1. A function **`orders-api`** (runtime `python3.12`, handler
   `handler.handler`, the role `orders-api-fn`) from `v1.zip`,
   **published** as version 1.
2. An alias **`live`** pointing at version **1**.
3. The code from `v2.zip`, published as version **2**, with different code
   from version 1. The alias stays on 1: moving it is CodeDeploy's job.
4. An alarm **`orders-api-errors`**: `AWS/Lambda` `Errors` with the
   dimensions `FunctionName=orders-api` and `Resource=orders-api:live`,
   `Sum` over **60** s, **1** evaluation period, `GreaterThanThreshold`
   **0**, missing data `notBreaching`.
5. A role **`codedeploy-orders-api`** trusted by `codedeploy.amazonaws.com`
   with `service-role/AWSCodeDeployRoleForLambda`.
6. A CodeDeploy application **`orders-api`** for the compute platform
   **`Lambda`**, and a deployment group **`live`** with that role:
   `CodeDeployDefault.LambdaCanary10Percent5Minutes`, `BLUE_GREEN` with
   `WITH_TRAFFIC_CONTROL`, automatic rollback **enabled** on both
   `DEPLOYMENT_FAILURE` and `DEPLOYMENT_STOP_ON_ALARM`, and the alarm
   `orders-api-errors` attached (the emulator does not report the alarm
   back, so the check skips that part, but set it).
7. **`appspec.yml`** (edit the file): version `0.0`, **one** resource of
   type `AWS::Lambda::Function` for `orders-api` on `live`, from version
   `"1"` to `"2"`, with `orders-api-smoke` as the **`BeforeAllowTraffic`**
   hook.

After **Run**:

```
$ aws deploy get-deployment-group --application-name orders-api --deployment-group-name live \
    --query 'deploymentGroupInfo.[deploymentConfigName,deploymentStyle]'
[
    "CodeDeployDefault.LambdaCanary10Percent5Minutes",
    {
        "deploymentType": "BLUE_GREEN",
        "deploymentOption": "WITH_TRAFFIC_CONTROL"
    }
]
```

The emulator does not run deployments, so the release itself stops here; in
AWS, `create-deployment` with this AppSpec would start the canary.

## Check yourself

1. Why do callers use the alias `live` instead of version 2's ARN?
   *A release then moves one pointer; callers never change, and a rollback
   is moving it back.*
2. What is the difference between `LambdaCanary10Percent5Minutes` and
   `LambdaLinear10PercentEvery1Minute`?
   *Canary: 10%, then everything after 5 minutes. Linear: 10% more every
   minute.*
3. The `BeforeAllowTraffic` hook finds a bug. What do users see?
   *Nothing: no traffic has moved yet, and the deployment rolls back.*
4. Why is the alarm's missing data `notBreaching`?
   *A minute with no invocations has no `Errors` data, and that is not a
   failure.*
5. In a real account, the deployment fails at `BeforeAllowTraffic` with
   `AccessDenied` invoking `orders-api-smoke`. Why?
   *`AWSCodeDeployRoleForLambda` only invokes functions named
   `CodeDeployHook_*`; rename the hook, or grant the role
   `lambda:InvokeFunction` on it.*
