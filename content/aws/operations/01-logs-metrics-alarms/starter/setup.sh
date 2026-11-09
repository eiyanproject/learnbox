#!/usr/bin/env bash
# Operations 1: logs, metrics and alarms.
set -euo pipefail

# 1. Log group /app/web, 30 days of retention.


# 2. Metric filter errors: pattern ERROR -> Learnbox/AppErrors, value 1, default 0.


# 3. SNS topic ops-alerts, email subscription for ops@example.com.


# 4. Alarm app-errors: Sum of AppErrors over 300 s, 1 period, >= 5,
#    missing data notBreaching, to ops-alerts.


# 5. Alarm high-cpu: Average AWS/EC2 CPUUtilization for AutoScalingGroupName=web-asg,
#    300 s, 3 periods, > 80, to ops-alerts.

