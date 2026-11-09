#!/usr/bin/env bash
# Operations 1: logs, metrics and alarms.
set -euo pipefail

# 1. Log group /app/web, 30 days of retention.
aws logs create-log-group --log-group-name /app/web
aws logs put-retention-policy --log-group-name /app/web --retention-in-days 30

# 2. Metric filter errors: pattern ERROR -> Learnbox/AppErrors, value 1, default 0.
aws logs put-metric-filter --log-group-name /app/web --filter-name errors \
  --filter-pattern ERROR \
  --metric-transformations metricName=AppErrors,metricNamespace=Learnbox,metricValue=1,defaultValue=0

# 3. SNS topic ops-alerts, email subscription for ops@example.com.
TOPIC=$(aws sns create-topic --name ops-alerts --query TopicArn --output text)
aws sns subscribe --topic-arn "$TOPIC" --protocol email \
  --notification-endpoint ops@example.com >/dev/null

# 4. Alarm app-errors: Sum of AppErrors over 300 s, 1 period, >= 5,
#    missing data notBreaching, to ops-alerts.
aws cloudwatch put-metric-alarm --alarm-name app-errors \
  --namespace Learnbox --metric-name AppErrors --statistic Sum \
  --period 300 --evaluation-periods 1 --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching --alarm-actions "$TOPIC"

# 5. Alarm high-cpu: Average AWS/EC2 CPUUtilization for AutoScalingGroupName=web-asg,
#    300 s, 3 periods, > 80, to ops-alerts.
aws cloudwatch put-metric-alarm --alarm-name high-cpu \
  --namespace AWS/EC2 --metric-name CPUUtilization --statistic Average \
  --dimensions Name=AutoScalingGroupName,Value=web-asg \
  --period 300 --evaluation-periods 3 --threshold 80 \
  --comparison-operator GreaterThanThreshold --alarm-actions "$TOPIC"
