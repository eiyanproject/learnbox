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

An **Auto Scaling group** keeps a number of instances running from a launch
template, across the subnets you give it:

- **Self-healing**: an instance that fails its health check is terminated
  and replaced.
- **Elastic**: capacity moves between **min** and **max**, aiming at
  **desired**, as policies change it.
- **Balanced**: instances are spread across the group's Availability Zones.

## Health checks

By default the group only asks EC2 whether the instance is running. Behind
a load balancer, use **ELB health checks**, so an instance whose web server
has died - running, but failing `/health` - is replaced too. The **grace
period** gives a new instance time to boot before checks count.

## Scaling policies

| Policy | Does | Use |
|---|---|---|
| **Target tracking** | keeps a metric at a value (CPU at 50%, requests per target at 1,000) | the default choice |
| **Step** | adds or removes amounts as an alarm crosses thresholds | fine-grained control |
| **Scheduled** | sets capacity at times you know | known peaks |
| **Predictive** | forecasts daily and weekly patterns | recurring load |

A group can combine them: scheduled actions raise the floor before the
morning peak, and target tracking handles whatever the day brings.

## Your task

The script already makes the VPC, the launch template **web** and the target
group **web-tg** (from the last two lessons). Add:

1. an Auto Scaling group **`web-asg`** from the template's **default
   version**, in **private-a and private-b**, **min 2, max 6, desired 2**,
   registered with **web-tg**, using **ELB health checks** with a **300**
   second grace period;
2. a **target tracking** policy keeping **average CPU at 50%**;
3. a scheduled action **`weekday-morning`** at **07:45 UTC Monday to
   Friday** setting min and desired to **4**, and **`weekday-evening`** at
   **19:00 UTC Monday to Friday** setting them back to **2**.
