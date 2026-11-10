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


# 2. Roles orders-api-execution (AmazonECSTaskExecutionRolePolicy) and
#    orders-api-task (DynamoDB on the orders table only).


# 3. Cluster apps with Container Insights.


# 4. Task definition orders-api: Fargate, awsvpc, 512 CPU / 1024 MiB, port
#    8080, awslogs, DB_PASSWORD from the secret, both roles.


# 5. Security group orders-api: 8080 from 10.0.0.0/16.


# 6. Service orders-api: 2 tasks, private subnets, no public IP.


# 7. update-service: circuit breaker with rollback, 100% / 200%.


# 8. Auto scaling 2-10 on average CPU 60%.

