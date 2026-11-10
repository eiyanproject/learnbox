---
title: An ECS service on Fargate
summary: A cluster with Container Insights, a task definition with separate execution and task roles, logs and a secret, a service in private subnets that rolls back failed deployments by itself, and auto scaling on CPU.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "Both roles trust `ecs-tasks.amazonaws.com`. Attach `arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy` to the execution role; put the DynamoDB statement inline on the task role."
  - "Write the task definition as JSON with python3 and register it with `aws ecs register-task-definition --cli-input-json file://taskdef.json`. A secret is `\"secrets\": [{\"name\": \"DB_PASSWORD\", \"valueFrom\": \"<secret ARN>\"}]` inside the container definition."
  - "`aws ecs create-service --cluster apps --service-name orders-api --task-definition orders-api --desired-count 2 --launch-type FARGATE --network-configuration \"awsvpcConfiguration={subnets=[$PRIVATE_A,$PRIVATE_B],securityGroups=[$SG],assignPublicIp=DISABLED}\"` - double quotes, so the variables expand."
  - "`aws ecs update-service --cluster apps --service orders-api --deployment-configuration 'deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200'`."
  - "Scaling goes through Application Auto Scaling: `aws application-autoscaling register-scalable-target --service-namespace ecs --resource-id service/apps/orders-api --scalable-dimension ecs:service:DesiredCount --min-capacity 2 --max-capacity 10`, then `put-scaling-policy` with `--policy-type TargetTrackingScaling` and `PredefinedMetricType: ECSServiceAverageCPUUtilization`."
---

**Amazon ECS** runs containers; **Fargate** runs them without servers to
manage - you choose CPU and memory per task and pay for those, by the
second. (ECS on EC2 is the alternative when you need GPUs, special
instance types, or cheaper dense packing at scale.)

## The pieces

- A **cluster** is a namespace for services and tasks. Turn on **Container
  Insights** for per-task CPU, memory and network metrics.
- A **task definition** is the versioned recipe: image, CPU and memory,
  ports, environment, secrets, logging, and two roles.
- A **service** keeps N copies of a task running, replaces failed ones,
  registers them with a load balancer, and rolls out new revisions.

## Two roles, two jobs

| Role | Used by | For |
|---|---|---|
| **Execution role** | the ECS agent | pulling the image from ECR, writing logs, fetching `secrets` at start-up |
| **Task role** | your application code | whatever the application calls - DynamoDB, S3, SQS |

Mixing them up is a classic mistake: the application should not be able to
pull arbitrary images, and the agent does not need your table.

## Networking: awsvpc

Fargate tasks use `awsvpc` networking: each task gets its own network
interface and private IP in your subnets, and its own **security group**.
Run them in **private subnets** with no public IP; they reach ECR, logs and
Secrets Manager through a NAT gateway or VPC endpoints.

## Deployments that undo themselves

A rolling update with `minimumHealthyPercent 100` and `maximumPercent 200`
starts new tasks before stopping old ones, so capacity never drops. The
**deployment circuit breaker** watches the new tasks: if they keep failing
to start or to pass health checks, it marks the deployment failed and, with
`rollback`, returns to the last working revision. For blue/green with a
test listener, use CodeDeploy (section 9).

## Scaling

Services scale through **Application Auto Scaling**: register the service's
desired count as a scalable target with a minimum and maximum, then attach
a **target tracking** policy (average CPU, memory, or ALB requests per
target).

## Your task

Done for you: the foundations VPC (`awslab given vpc`), and a secret
`prod/orders/db`.

1. A log group **`/ecs/orders-api`** with **30 days** retention.
2. Roles trusted by `ecs-tasks.amazonaws.com`: **`orders-api-execution`**
   with `AmazonECSTaskExecutionRolePolicy`, and **`orders-api-task`** with an
   inline policy allowing `dynamodb:GetItem`, `PutItem`, `UpdateItem` and
   `Query` on the table `orders` only.
3. A cluster **`apps`** with **Container Insights** enabled.
4. A task definition **`orders-api`** for **Fargate**: `awsvpc`, **512** CPU
   units and **1024** MiB; one container `orders-api` running
   `ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-1` on port
   **8080**, logging to the group above with the `awslogs` driver, and the
   secret's ARN injected as **`DB_PASSWORD`**; both roles set.
5. A security group **`orders-api`** allowing TCP **8080** from
   `10.0.0.0/16` only.
6. A service **`orders-api`** in `apps`: **2** tasks on Fargate in the two
   **private** subnets, **no public IP**.
7. Then change the service in place, as you would one that already runs:
   `update-service` with the circuit breaker **with rollback**, minimum
   healthy **100%**, maximum **200%**. (Set these at creation in real
   projects; the emulator only keeps them from an update.)
8. Auto scaling from **2** to **10** tasks with target tracking on average
   CPU at **60%**.
