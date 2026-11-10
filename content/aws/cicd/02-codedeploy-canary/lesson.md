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

Deploying a new Lambda version by pointing everyone at it is all or
nothing. **CodeDeploy** shifts the traffic gradually and watches while it
does.

## Versions and aliases

`publish-version` freezes the function's code and configuration as an
immutable, numbered **version**. An **alias** (`live`) is a named pointer to
a version - callers and event sources use the alias, never `$LATEST`. An
alias can split traffic between two versions with **weights**, and that is
what CodeDeploy drives.

## Deployment configurations

| Configuration | What happens |
|---|---|
| `LambdaCanary10Percent5Minutes` | 10% to the new version, then all of it after 5 minutes |
| `LambdaLinear10PercentEvery1Minute` | +10% every minute |
| `LambdaAllAtOnce` | everything at once (still with hooks and rollback) |

## Hooks and rollback

The **AppSpec** names the function, alias, current and target versions,
and **hooks**: Lambda functions CodeDeploy invokes **BeforeAllowTraffic**
(test the new version before it gets any traffic) and
**AfterAllowTraffic**. A hook reports success or failure with
`PutLifecycleEventHookExecutionStatus`.

**Automatic rollback** returns the alias to the old version when the
deployment fails, or when a CloudWatch alarm on the deployment group goes
into ALARM - here, any error on the `live` alias. That turns "watch the
graphs after a deploy" into something the system does.

The same model deploys ECS services (with a test listener) and EC2 fleets
(with lifecycle scripts) - see the DOP practice questions.

## Your task

Done for you: the role `orders-api-fn`, the code of both versions
(`v1.zip`, `v2.zip`), and the smoke-test function **`orders-api-smoke`**.

1. A function **`orders-api`** (python3.12, `handler.handler`, the role
   `orders-api-fn`) from `v1.zip`, **published** as version 1.
2. An alias **`live`** pointing at version **1**.
3. The code from `v2.zip`, published as version **2** (the alias stays on
   1 - moving it is CodeDeploy's job).
4. An alarm **`orders-api-errors`**: `AWS/Lambda` `Errors` for the
   `live` alias (dimensions `FunctionName=orders-api`,
   `Resource=orders-api:live`), Sum over 60 s, above **0** for **1**
   period, missing data not breaching.
5. A role **`codedeploy-orders-api`** trusted by
   `codedeploy.amazonaws.com` with
   `service-role/AWSCodeDeployRoleForLambda`.
6. A CodeDeploy application **`orders-api`** for **Lambda**, and a
   deployment group **`live`**: `LambdaCanary10Percent5Minutes`, blue/green
   with traffic control, automatic rollback on **failure** and on
   **alarm**, with the alarm `orders-api-errors`.
7. **`appspec.yml`** (edit the file) describing the release of
   `orders-api` on `live` from version **1** to **2**, with
   `orders-api-smoke` as the **BeforeAllowTraffic** hook.
