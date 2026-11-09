---
title: Logs, metrics and alarms
summary: CloudWatch from the ground up - a log group with retention, a metric filter that turns log lines into a metric, and alarms that tell an SNS topic when errors or CPU climb.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws logs create-log-group --log-group-name /app/web`, then `aws logs put-retention-policy --log-group-name /app/web --retention-in-days 30`."
  - "`aws logs put-metric-filter --log-group-name /app/web --filter-name errors --filter-pattern ERROR --metric-transformations metricName=AppErrors,metricNamespace=Learnbox,metricValue=1,defaultValue=0`."
  - "`aws cloudwatch put-metric-alarm --alarm-name app-errors --namespace Learnbox --metric-name AppErrors --statistic Sum --period 300 --evaluation-periods 1 --threshold 5 --comparison-operator GreaterThanOrEqualToThreshold --treat-missing-data notBreaching --alarm-actions \"$TOPIC\"`."
  - "The CPU alarm needs a dimension: `--dimensions Name=AutoScalingGroupName,Value=web-asg`, with `--statistic Average --period 300 --evaluation-periods 3 --threshold 80 --comparison-operator GreaterThanThreshold`."
---

**CloudWatch** is where AWS keeps the numbers and the logs.

## Metrics

A **metric** is a time series in a **namespace** (`AWS/EC2`,
`AWS/ApplicationELB`, or your own), identified by its name and
**dimensions** - `CPUUtilization` for `AutoScalingGroupName=web-asg`. AWS
services publish theirs automatically: EC2 every 5 minutes by default (1
minute with detailed monitoring). Memory and disk use are *inside* the
instance, so EC2 cannot see them - the **CloudWatch agent** publishes those.

## Logs

**CloudWatch Logs** stores log events in **log groups** (one per
application or function) made of **streams** (one per instance or
container). Lambda writes to `/aws/lambda/<function>` by itself. Log groups
keep everything **forever** unless you set a **retention period** - a classic
source of a slowly growing bill.

A **metric filter** turns matching log lines into a metric: count every line
containing `ERROR`, and the error rate becomes something you can graph and
alarm on. **Logs Insights** queries logs ad hoc.

## Alarms

An **alarm** watches one metric (or a math expression) and changes state -
`OK`, `ALARM`, `INSUFFICIENT_DATA` - when it crosses a threshold for a number
of **evaluation periods**. On a state change it can notify an **SNS topic**,
scale an Auto Scaling group, or stop, reboot or recover an instance.

**Treat missing data** matters for sparse metrics: an error count that is
only published when errors happen has *no data* most of the time, which
should count as fine (`notBreaching`), not as unknown.

## Your task

1. A log group **`/app/web`** keeping logs **30 days**.
2. A metric filter **`errors`** on it: pattern **`ERROR`**, publishing
   **`AppErrors`** in the namespace **`Learnbox`**, value **1** (default 0).
3. An SNS topic **`ops-alerts`** with an **email** subscription for
   **ops@example.com** (it stays pending until confirmed - fine here).
4. An alarm **`app-errors`**: **Sum** of `AppErrors` over **300** s, **1**
   period, **>= 5**, missing data **notBreaching**, notifying `ops-alerts`.
5. An alarm **`high-cpu`**: **Average** `CPUUtilization` (`AWS/EC2`) for
   **AutoScalingGroupName=web-asg** over **300** s, **3** periods, **> 80**,
   notifying `ops-alerts`.

After **Run**, push a log line and look at it:

```
aws logs create-log-stream --log-group-name /app/web --log-stream-name test
aws logs put-log-events --log-group-name /app/web --log-stream-name test \
  --log-events timestamp=$(date +%s000),message="ERROR payment declined"
aws logs filter-log-events --log-group-name /app/web --filter-pattern ERROR
```
