---
title: Auto Scaling groups
summary: Instances that replace themselves and follow the load - a group across two AZs behind the load balancer, ELB health checks, target tracking on CPU, and scheduled capacity for a known morning peak.
order: 3
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws autoscaling create-auto-scaling-group --auto-scaling-group-name web-asg --launch-template 'LaunchTemplateName=web,Version=$Default' --min-size 2 --max-size 6 --desired-capacity 2 --vpc-zone-identifier \"$PRIVATE_A,$PRIVATE_B\" --target-group-arns \"$TG\" --health-check-type ELB --health-check-grace-period 300`."
  - "Target tracking: `aws autoscaling put-scaling-policy --auto-scaling-group-name web-asg --policy-name cpu-50 --policy-type TargetTrackingScaling --target-tracking-configuration '{\"PredefinedMetricSpecification\":{\"PredefinedMetricType\":\"ASGAverageCPUUtilization\"},\"TargetValue\":50}'`."
  - "Scheduled actions take a cron expression in UTC: `aws autoscaling put-scheduled-update-group-action --auto-scaling-group-name web-asg --scheduled-action-name weekday-morning --recurrence '45 7 * * 1-5' --min-size 4 --desired-capacity 4`."
  - "The evening action sets `--min-size 2 --desired-capacity 2` at `0 19 * * 1-5`, so target tracking can scale back in."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **Auto Scaling group** | keeps instances running from a launch template, replacing and adding them as needed |
| **self-healing** | a failed instance is replaced automatically |
| **elastic** | the number of instances follows the load |
| **min** / **desired** / **max** | never fewer / how many now / the ceiling |
| **desired capacity** | the number the group aims at; policies move it |
| **AZ rebalancing** | spreading instances evenly over AZs; may briefly exceed max |
| **EC2 health check** | only asks whether the instance is running |
| **ELB health check** | also uses the target group's check, so a crashed web server is replaced |
| **grace period** | seconds a new instance gets before health checks count |
| **scaling policy** | the rule that changes desired capacity |
| **target tracking** | keeps a metric at a value, such as average CPU at 50% |
| **step scaling** | adds or removes set amounts as an alarm crosses thresholds |
| **scheduled action** | sets min, max or desired at chosen times |
| **predictive scaling** | forecasts daily and weekly patterns and scales ahead |
| **scale out** / **scale in** | add / remove instances |
| **scale up** | use a bigger instance type instead |
| **metric** | a measured number over time, such as CPU |
| **`ASGAverageCPUUtilization`** | the average CPU of the group's instances |
| **`RequestCountPerTarget`** | requests per target, from the load balancer |
| **cron expression** | five fields (minute hour day month weekday), always UTC: `45 7 * * 1-5` |
| **UTC** | Coordinated Universal Time |
| **cooldown** / **warm-up** | time for new instances to start and metrics to settle before the next decision |
| **unbound variable** | `set -u` stopping on `$Default`, which the shell read as a variable |
| **single quotes** | pass text to a command untouched: `'Version=$Default'` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws autoscaling create-auto-scaling-group --auto-scaling-group-name N --launch-template 'LaunchTemplateName=web,Version=$Default' --vpc-zone-identifier "A,B" --min-size 2 --max-size 6 --desired-capacity 2` | creates the group |
| `--target-group-arns T` | registers its instances with the target group |
| `--health-check-type ELB --health-check-grace-period 300` | ELB health checks with a grace period |
| `aws autoscaling put-scaling-policy --policy-type TargetTrackingScaling --target-tracking-configuration file://...` | adds a target tracking policy |
| `aws autoscaling put-scheduled-update-group-action --scheduled-action-name N --recurrence '45 7 * * 1-5' --min-size 4 --desired-capacity 4` | adds a scheduled action |
| `aws autoscaling describe-scheduled-actions --auto-scaling-group-name N` | lists them |
| `aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names N` | shows the group and its instances |

### Errors

| Error | Means |
|---|---|
| `Default: unbound variable` | `$Default` in double quotes or unquoted, with `set -u` |
| `Invalid length for parameter LaunchTemplate.Version, value: 0` | the same mistake without `set -u`: the CLI got `Version=` |

---

The last two lessons gave the web tier a recipe (the launch template) and a
front door (the load balancer). What is missing is the servers themselves,
and someone to look after them: replace a server that dies at 3 a.m., add
servers when a sale starts, and remove them again afterwards so you stop
paying for them. An **Auto Scaling group** does all three.

It keeps a number of instances running from a launch template, in the
subnets you give it:

- **Self-healing**: an instance that fails its health check is terminated
  and a new one launched in its place, with no one paged.
- **Elastic**: the number of instances moves between a **minimum** and a
  **maximum**, aiming at a **desired capacity** that scaling policies change
  as the load changes.
- **Balanced**: instances are spread evenly across the group's Availability
  Zones, so losing one AZ loses only part of the capacity.

```text
 web-alb ──> target group web-tg ──> instances registered by the group
                                        ▲
 Auto Scaling group web-asg ────────────┘  launches from template web ($Default)
   min 2  desired 2  max 6                 in private-a and private-b
   policies:  CPU at 50%   +   07:45 UTC weekdays: min 4   +   19:00 UTC weekdays: min 2
```

The three numbers:

| | Meaning |
|---|---|
| **min** | never fewer than this, whatever the policies say |
| **desired** | how many there should be right now; policies move it |
| **max** | the ceiling for scaling, and so for the bill (only while rebalancing AZs may the group briefly exceed it, by 10% or one instance) |

With min 2 and two AZs, an AZ failure still leaves one instance serving
while replacements start.

## Health checks

By default the group only asks EC2 whether each instance is running. An
instance whose web server has crashed is still "running", so it would stay,
serving errors. Behind a load balancer, use **ELB health checks** instead:
the group then also treats an instance as unhealthy when the target group's
health check (`GET /health`, from lesson 2) fails, and replaces it.

The **grace period** (here 300 seconds) gives a new instance time to boot
and run its user data before health checks count against it. Too short, and
the group replaces instances that are still installing nginx, forever.

## Scaling policies

Policies decide when the desired capacity changes:

| Policy | Does | Use it for |
|---|---|---|
| **Target tracking** | keeps a metric at a target value, such as average CPU at 50%, or 1,000 requests per target | the default choice: you name the goal, AWS does the arithmetic |
| **Step scaling** | adds or removes set amounts as an alarm crosses thresholds | fine-grained control over how fast it reacts |
| **Scheduled** | sets min, max or desired at times you choose | load you **know** is coming |
| **Predictive** | forecasts daily and weekly patterns from history and scales ahead of them | recurring load |

They combine. Here, scheduled actions raise the **floor** before the known
morning peak (min 4 from 07:45, so the instances are booted and warm when
the users arrive at 08:00), and target tracking handles whatever else the
day brings. In the evening, the floor goes back down to 2, and target
tracking is then free to **scale in** to 2 again as the CPU falls.

A target tracking policy is configured with a small JSON document:

```json
{"PredefinedMetricSpecification": {"PredefinedMetricType": "ASGAverageCPUUtilization"}, "TargetValue": 50}
```

`ASGAverageCPUUtilization` is the average CPU of all instances in the group.

### Cron expressions

A scheduled action's `--recurrence` is a **cron expression**, five fields
separated by spaces, always in **UTC**:

```text
 minute  hour  day-of-month  month  day-of-week
   45     7         *          *        1-5        = 07:45 UTC, Monday to Friday
```

`*` means "every", and days of the week are numbered from 0 (Sunday), so
`1-5` is Monday to Friday. Write the expression in single quotes, so the
shell does not expand the `*`s into file names.

## Quoting `$Default`

The group follows the template's **default** version, written
`Version=$Default`. That `$` is trouble in a shell script: in double quotes,
or unquoted, the shell treats `$Default` as a variable, finds none, and
substitutes nothing. With the starter's `set -u` the script stops with
`Default: unbound variable`; without it, the CLI receives `Version=` and
refuses:

```
Parameter validation failed:
Invalid length for parameter LaunchTemplate.Version, value: 0, valid min length: 1
```

Single quotes pass the text through untouched:

```
--launch-template 'LaunchTemplateName=web,Version=$Default'
```

## More about scaling

- **Scaling out** (more instances) is what Auto Scaling does; **scaling up**
  (a bigger instance type) suits things that cannot be split, like a single
  database.
- After a scaling action, a **cooldown** (300 seconds by default) lets the
  new instances start and the metrics settle before the next simple-scaling
  decision; target tracking uses a similar instance **warm-up**.
- Good metrics to scale on: average CPU, `RequestCountPerTarget` from the
  load balancer, network in and out, or, for queue workers, the queue length
  (`ApproximateNumberOfMessagesVisible`, Serverless lesson 1).
- Auto Scaling itself is free; you pay for the instances.

## Your task

The script already makes the VPC, the launch template **web** and the
target group **web-tg** (in `TG`), as in the last two lessons. Add:

1. an Auto Scaling group **`web-asg`**:
   - launching from the template **web**, following its **`$Default`**
     version;
   - in **private-a and private-b** (`--vpc-zone-identifier` takes the
     subnet IDs as one comma-separated string);
   - **min 2, max 6, desired 2**;
   - registering its instances with **web-tg** (`--target-group-arns`);
   - using **ELB** health checks with a **300**-second grace period;
2. a **target tracking** policy keeping **average CPU** at **50**;
3. two scheduled actions:
   - **`weekday-morning`**, at **07:45 UTC Monday to Friday**
     (`45 7 * * 1-5`), setting min and desired to **4**;
   - **`weekday-evening`**, at **19:00 UTC Monday to Friday**
     (`0 19 * * 1-5`), setting them back to **2**.

After **Run**:

```
$ aws autoscaling describe-scheduled-actions --auto-scaling-group-name web-asg \
    --query 'ScheduledUpdateGroupActions[].[ScheduledActionName,Recurrence,MinSize,DesiredCapacity]' --output table
-----------------------------------------------
|          DescribeScheduledActions           |
+------------------+----------------+----+----+
|  weekday-morning |  45 7 * * 1-5  |  4 |  4 |
|  weekday-evening |  0 19 * * 1-5  |  2 |  2 |
+------------------+----------------+----+----+
```

`aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names
web-asg` shows the group with its two instances. (The emulator launches
them, but may put both in one AZ; real Auto Scaling balances them across
private-a and private-b. Nothing is ever really scaled here, since there is
no CPU load to measure.)

## Check yourself

1. What do min, desired and max mean?
   *The floor, the current target count, and the ceiling.*
2. Why use ELB health checks rather than EC2 ones behind a load balancer?
   *A running instance whose web server crashed passes EC2 checks but fails
   the load balancer's.*
3. Why is `$Default` written in single quotes?
   *Otherwise the shell treats it as an (empty) variable.*
4. The morning peak is at 08:00 every weekday. Which policy prepares for it?
   *A scheduled action shortly before, raising the minimum.*
