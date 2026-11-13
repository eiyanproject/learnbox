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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **CloudWatch** | where AWS keeps metrics, logs and alarms |
| **metric** | a series of numbers over time, such as CPU use every 5 minutes |
| **namespace** | a group of related metrics: `AWS/EC2`, or your own such as `Learnbox` |
| **dimension** | a name-value pair saying which thing a metric measures: `AutoScalingGroupName=web-asg` |
| **detailed monitoring** | EC2 metrics every minute instead of every 5 |
| **CloudWatch agent** | software on the instance that publishes memory and disk use, which EC2 cannot see |
| **log event** | one log line, with a timestamp |
| **log group** | logs of one application or function |
| **log stream** | one source within a group, such as one instance |
| **retention period** | how long a log group keeps events (1 day to 10 years); forever if unset |
| **metric filter** | counts log events matching a pattern into a metric; not retroactive |
| **filter pattern** | the text to match, such as `ERROR` |
| **default value** | published for periods with events but no matches, so the metric has no gaps |
| **Logs Insights** | queries stored logs with a query language |
| **alarm** | watches a metric and acts when it crosses a threshold |
| **`OK`**, **`ALARM`**, **`INSUFFICIENT_DATA`** | an alarm's three states |
| **threshold** | the value an alarm compares against |
| **period** | the length of each data window, in seconds |
| **statistic** | how points in a period are combined: `Average`, `Sum`, `Maximum` |
| **breaching** | a period on the wrong side of the threshold |
| **evaluation periods** | how many periods are looked at; "datapoints to alarm" sets M of N |
| **sparse metric** | one that only has data when something happens |
| **treat missing data** | how an alarm counts periods with no data: `missing` (default), `notBreaching`, `breaching`, `ignore` |
| **pending confirmation** | an email subscription waiting for the recipient's click |
| **export to S3** / **subscription filter** | batch / real-time ways to send logs elsewhere |
| **Kinesis**, **Firehose** | streaming services logs can be sent to |
| **composite alarm** | combines alarms with AND and OR |
| **status check** | EC2's health check of an instance and its host; an alarm on it can recover the instance |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws logs create-log-group --log-group-name /app/web` | creates a log group |
| `aws logs put-retention-policy --log-group-name G --retention-in-days 30` | sets retention |
| `aws logs put-metric-filter --log-group-name G --filter-name N --filter-pattern ERROR --metric-transformations ...` | creates a metric filter |
| `aws logs create-log-stream --log-group-name G --log-stream-name S` | creates a stream |
| `aws logs put-log-events --log-group-name G --log-stream-name S --log-events timestamp=...,message=...` | writes log lines |
| `aws logs filter-log-events --log-group-name G --filter-pattern ERROR` | searches stored events |
| `aws sns subscribe --topic-arn T --protocol email --notification-endpoint ADDRESS` | an email subscription |
| `aws cloudwatch put-metric-alarm --alarm-name N --namespace NS --metric-name M --statistic Sum --period 300 --evaluation-periods 1 --threshold 5 --comparison-operator GreaterThanOrEqualToThreshold --alarm-actions T` | creates an alarm |
| `--dimensions Name=AutoScalingGroupName,Value=web-asg` | which thing the metric is about |
| `--treat-missing-data notBreaching` | no data counts as fine |
| `aws cloudwatch describe-alarms` | lists alarms and states |
| `aws cloudwatch set-alarm-state --alarm-name N --state-value ALARM --state-reason testing` | forces a state, to test the action |
| `$(date +%s000)` | the time in milliseconds |

---

The earlier sections built a web tier, a database and a queue. Once real
users arrive, the questions change: is it working right now? Is it getting
slower? Did errors start after this morning's deploy? And, most of all:
will someone **find out** when it breaks, before the customers do?
**CloudWatch** is where AWS keeps the numbers (**metrics**) and the text
(**logs**) that answer those questions, and the **alarms** that tell someone.

This lesson wires up all three for the web application:

```text
 app writes log lines ──> log group /app/web (kept 30 days)
                              │ metric filter "errors": each line containing ERROR counts 1
                              v
                         metric Learnbox/AppErrors ──> alarm app-errors (>= 5 in 5 minutes) ──┐
 EC2 publishes ──> metric AWS/EC2 CPUUtilization (web-asg) ──> alarm high-cpu (> 80% for 15 min) ┤
                                                                                              v
                                                                  SNS topic ops-alerts ──> email ops@example.com
```

## Metrics

A **metric** is a series of numbers over time, such as "CPU use, every 5
minutes". Each metric lives in a **namespace**, a group of related metrics
(`AWS/EC2` for EC2's, `AWS/ApplicationELB` for load balancers', or your own,
like `Learnbox`), and is identified by its **name** and its **dimensions**:
name-value pairs saying *which* thing it measures. `CPUUtilization` with
`AutoScalingGroupName=web-asg` is the average CPU of that group's
instances; with `InstanceId=i-...` it is one instance's.

AWS services publish their metrics automatically: EC2 every 5 minutes by
default, every minute with **detailed monitoring**. Memory and disk use are
**inside** the instance's operating system, where EC2 cannot see them; the
**CloudWatch agent**, installed on the instance, publishes those. ("Why is
there no memory metric for my instance?" is a classic exam question.)

## Logs

**CloudWatch Logs** stores log lines (**log events**) in **log groups**,
usually one per application or function, each made of **log streams**,
usually one per instance or container. Lambda writes to
`/aws/lambda/<function name>` by itself.

💸 A log group keeps everything **forever** unless you give it a
**retention period** (1 day to 10 years), and stored logs are billed per GB
per month. A group nobody set retention on is a classic slowly growing
bill.

### Metric filters

Logs are text, and alarms watch numbers. A **metric filter** connects them:
it watches a log group, and for every log event matching a **filter
pattern**, adds a value to a metric. With pattern `ERROR` and value `1`,
each line containing `ERROR` counts one, and the error rate becomes a
metric you can graph and alarm on. Its `defaultValue` of `0` is published
for periods with log events but no matches, so the metric reads "0 errors"
instead of having gaps.

```
$ aws logs filter-log-events --log-group-name /app/web --filter-pattern ERROR \
    --query 'events[].message'
[
    "ERROR payment declined"
]
```

A metric filter is **not retroactive**: it only counts log events that
arrive after it was created, so errors from before it existed never appear
in the metric.

(`filter-log-events` searches stored events with the same pattern syntax.
For anything more complex, **Logs Insights** runs queries over logs.)

## Alarms

An **alarm** watches one metric (or a calculation over several) and is in
one of three **states**: `OK`, `ALARM`, or `INSUFFICIENT_DATA` (not enough
data to decide, as for a brand-new alarm). It changes state when the metric
crosses a **threshold** for a number of periods, and on each change it can
**act**: notify an SNS topic, scale an Auto Scaling group, or stop, reboot
or recover an instance.

Reading `put-metric-alarm`'s main options as a sentence, for `high-cpu`:

| Option | Value | Meaning |
|---|---|---|
| `--statistic` | `Average` | combine the data points in each period by averaging (`Sum` for counts, `Maximum` for peaks) |
| `--period` | `300` | each period is 300 seconds (5 minutes) |
| `--comparison-operator`, `--threshold` | `GreaterThanThreshold`, `80` | a period is "breaching" when the average is above 80 |
| `--evaluation-periods` | `3` | go to `ALARM` after 3 breaching periods in a row: 15 minutes, so a short spike does not page anyone (`--datapoints-to-alarm 2` would mean "2 of the last 3", for an "M out of N" alarm) |
| `--alarm-actions` | the topic's ARN | notify this SNS topic on entering `ALARM` |

### Treat missing data

Some metrics are **sparse**: `AppErrors` only gets data when the app logs
something. When nothing is logged at all, there is **no data**, and by
default (the `missing` setting) an alarm with no data goes to `INSUFFICIENT_DATA`, which would make
the error alarm look broken every quiet night. `--treat-missing-data
notBreaching` says "no data counts as fine". (The other choices are
`breaching`, for metrics where silence itself is bad, `ignore` and
`missing`.)

### Notifying people

The alarm notifies an **SNS topic** (Serverless lesson 2), and the topic
delivers to its subscribers, here by **email**. An email subscription
stays **pending** until the recipient clicks the link in the confirmation
email SNS sends, and until then nothing is delivered to it. In this sandbox
no email is sent, and that is fine for the check.

## More of CloudWatch

- **Logs Insights** queries stored logs with a query language, for
  investigations; it is not real-time.
- Logs leave CloudWatch in two ways: **export to S3** (batch, can take up to
  12 hours) or a **subscription filter** (real time, to Kinesis, Firehose or
  Lambda).
- Log groups are **encrypted** by default; a KMS key of your own is
  optional.
- The CloudWatch agent on an instance needs an **IAM role** allowing it to
  publish metrics and logs.
- A **composite alarm** combines several alarms with AND and OR ("CPU high
  AND errors high"), to cut noise.
- An alarm on an instance's **status check** can **recover** the instance
  onto new hardware, keeping its IP addresses.
- To test that an alarm's action works, force its state:
  `aws cloudwatch set-alarm-state --alarm-name app-errors --state-value ALARM --state-reason testing`
  (try it after Run; the emulator supports it).

## Your task

1. A log group **`/app/web`** keeping logs for **30 days**.
2. A metric filter **`errors`** on it, with the pattern **`ERROR`**,
   publishing the metric **`AppErrors`** in the namespace **`Learnbox`**,
   value **1**, default value **0**.
3. An SNS topic **`ops-alerts`** with an **email** subscription for
   **`ops@example.com`**.
4. An alarm **`app-errors`**: the **Sum** of `Learnbox`/`AppErrors` over
   **300**-second periods, **1** evaluation period, threshold **5** with
   **`GreaterThanOrEqualToThreshold`** (5 or more errors in 5 minutes),
   missing data **notBreaching**, notifying `ops-alerts`.
5. An alarm **`high-cpu`**: the **Average** of `AWS/EC2`/`CPUUtilization`
   for the dimension **`AutoScalingGroupName=web-asg`**, over **300**-second
   periods, **3** evaluation periods, threshold **80** with
   **`GreaterThanThreshold`**, notifying `ops-alerts`.

After **Run**, push two log lines and search for the error:

```
aws logs create-log-stream --log-group-name /app/web --log-stream-name test
aws logs put-log-events --log-group-name /app/web --log-stream-name test \
  --log-events timestamp=$(date +%s000),message="ERROR payment declined" \
               timestamp=$(date +%s000),message="INFO ok"
aws logs filter-log-events --log-group-name /app/web --filter-pattern ERROR
```

(`$(date +%s000)` is the time in milliseconds, which log events need.) And
see the alarms:

```
$ aws cloudwatch describe-alarms --query 'MetricAlarms[].[AlarmName,StateValue,Threshold,ComparisonOperator]' --output table
---------------------------------------------------------------
|                       DescribeAlarms                        |
+------------+-----+-------+----------------------------------+
|  app-errors|  OK |  5.0  |  GreaterThanOrEqualToThreshold   |
|  high-cpu  |  OK |  80.0 |  GreaterThanThreshold            |
+------------+-----+-------+----------------------------------+
```

(The emulator starts alarms at `OK`; real CloudWatch starts them at
`INSUFFICIENT_DATA` until the first data arrives.)

## Check yourself

1. Why is there no memory metric for an EC2 instance by default?
   *Memory is inside the operating system; the CloudWatch agent publishes
   it.*
2. What happens to logs in a group with no retention set?
   *They are kept forever, and billed.*
3. Why `notBreaching` for the error alarm?
   *No log lines means no data, which here means no errors.*
4. How long, at least, before `high-cpu` goes to ALARM?
   *15 minutes: three 5-minute periods in a row.*
