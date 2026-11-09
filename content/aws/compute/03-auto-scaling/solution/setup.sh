#!/usr/bin/env bash
# Compute 3: Auto Scaling groups.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# Done for you (lessons 1 and 2, cut down): the launch template web and the
# target group web-tg.
AMI_ID=$(aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].Value' --output text)
aws ec2 create-launch-template --launch-template-name web --launch-template-data \
  "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"t3.micro\",\"MetadataOptions\":{\"HttpTokens\":\"required\"}}" >/dev/null
TG=$(aws elbv2 create-target-group --name web-tg --protocol HTTP --port 80 \
  --vpc-id "$VPC_ID" --health-check-path /health \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# 1. web-asg: template web ($Default), private-a and private-b, min 2 max 6
#    desired 2, in web-tg, ELB health checks with a 300 second grace period.
aws autoscaling create-auto-scaling-group --auto-scaling-group-name web-asg \
  --launch-template 'LaunchTemplateName=web,Version=$Default' \
  --min-size 2 --max-size 6 --desired-capacity 2 \
  --vpc-zone-identifier "$PRIVATE_A,$PRIVATE_B" \
  --target-group-arns "$TG" \
  --health-check-type ELB --health-check-grace-period 300

# 2. Target tracking: average CPU at 50%.
aws autoscaling put-scaling-policy --auto-scaling-group-name web-asg \
  --policy-name cpu-50 --policy-type TargetTrackingScaling \
  --target-tracking-configuration \
  '{"PredefinedMetricSpecification":{"PredefinedMetricType":"ASGAverageCPUUtilization"},"TargetValue":50}' >/dev/null

# 3. Scheduled: weekday-morning 07:45 UTC Mon-Fri -> min/desired 4;
#    weekday-evening 19:00 UTC Mon-Fri -> min/desired 2.
aws autoscaling put-scheduled-update-group-action --auto-scaling-group-name web-asg \
  --scheduled-action-name weekday-morning --recurrence '45 7 * * 1-5' \
  --min-size 4 --desired-capacity 4
aws autoscaling put-scheduled-update-group-action --auto-scaling-group-name web-asg \
  --scheduled-action-name weekday-evening --recurrence '0 19 * * 1-5' \
  --min-size 2 --desired-capacity 2
