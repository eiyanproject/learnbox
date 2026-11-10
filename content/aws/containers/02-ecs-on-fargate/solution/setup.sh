#!/usr/bin/env bash
# Containers 2: an ECS service on Fargate.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
# Done for you: the database secret.
SECRET_ARN=$(aws secretsmanager create-secret --name prod/orders/db \
  --secret-string '{"username":"orders","password":"from-the-last-lesson"}' \
  --query ARN --output text)

# 1. Log group /ecs/orders-api, 30 days.
aws logs create-log-group --log-group-name /ecs/orders-api
aws logs put-retention-policy --log-group-name /ecs/orders-api --retention-in-days 30

# 2. Roles orders-api-execution (AmazonECSTaskExecutionRolePolicy) and
#    orders-api-task (DynamoDB on the orders table only).
TRUST='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
EXEC_ARN=$(aws iam create-role --role-name orders-api-execution \
  --assume-role-policy-document "$TRUST" --query Role.Arn --output text)
aws iam attach-role-policy --role-name orders-api-execution \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
TASK_ARN=$(aws iam create-role --role-name orders-api-task \
  --assume-role-policy-document "$TRUST" --query Role.Arn --output text)
aws iam put-role-policy --role-name orders-api-task --policy-name orders-table \
  --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:PutItem\",\"dynamodb:UpdateItem\",\"dynamodb:Query\"],\"Resource\":\"arn:aws:dynamodb:us-east-1:$ACCOUNT:table/orders\"}]}"

# 3. Cluster apps with Container Insights.
aws ecs create-cluster --cluster-name apps \
  --settings name=containerInsights,value=enabled >/dev/null

# 4. Task definition orders-api.
python3 - "$ACCOUNT" "$EXEC_ARN" "$TASK_ARN" "$SECRET_ARN" > taskdef.json <<'PY'
import json, sys
account, execution, task, secret = sys.argv[1:]
print(json.dumps({
    "family": "orders-api",
    "requiresCompatibilities": ["FARGATE"],
    "networkMode": "awsvpc",
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": execution,
    "taskRoleArn": task,
    "containerDefinitions": [{
        "name": "orders-api",
        "image": f"{account}.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-1",
        "essential": True,
        "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
        "secrets": [{"name": "DB_PASSWORD", "valueFrom": secret}],
        "logConfiguration": {"logDriver": "awslogs", "options": {
            "awslogs-group": "/ecs/orders-api",
            "awslogs-region": "us-east-1",
            "awslogs-stream-prefix": "orders-api"}},
    }],
}, indent=2))
PY
aws ecs register-task-definition --cli-input-json file://taskdef.json >/dev/null

# 5. Security group orders-api: 8080 from 10.0.0.0/16.
SG=$(aws ec2 create-security-group --group-name orders-api \
  --description "orders-api tasks" --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG" \
  --protocol tcp --port 8080 --cidr 10.0.0.0/16 >/dev/null

# 6. Service orders-api: 2 tasks, private subnets, no public IP.
aws ecs create-service --cluster apps --service-name orders-api \
  --task-definition orders-api --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_A,$PRIVATE_B],securityGroups=[$SG],assignPublicIp=DISABLED}" >/dev/null

# 7. update-service: circuit breaker with rollback, 100% / 200%.
aws ecs update-service --cluster apps --service orders-api \
  --deployment-configuration "deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200" >/dev/null

# 8. Auto scaling 2-10 on average CPU 60%.
aws application-autoscaling register-scalable-target --service-namespace ecs \
  --resource-id service/apps/orders-api --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 --max-capacity 10
aws application-autoscaling put-scaling-policy --service-namespace ecs \
  --resource-id service/apps/orders-api --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-60 --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
  '{"TargetValue": 60.0, "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"}}' >/dev/null
