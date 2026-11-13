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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **ECS** | Elastic Container Service: AWS's scheduler for containers |
| **Fargate** | runs tasks without servers; you pay per task's CPU and memory, per second |
| **scheduler** | decides where and when containers run, and restarts them |
| **cluster** | a named group of services and tasks |
| **task definition** | a versioned recipe: image, CPU, memory, ports, environment, secrets, logs, roles |
| **revision** | each registered version of a task definition |
| **task** | one running copy of a task definition |
| **service** | keeps N tasks running and rolls out new revisions |
| **`run-task`** | starts a one-off task, such as a nightly job |
| **ECS on EC2** | tasks on your own instances, which you patch and scale |
| **CPU units** | 1/1024 vCPU: `512` is half a vCPU |
| **Fargate combinations** | only some CPU and memory pairs are allowed |
| **container definition** | one container: `image`, `portMappings`, `environment`, `secrets`, `logConfiguration` |
| **`awslogs`** | the log driver sending standard output to CloudWatch Logs |
| **standard output** | what a program prints |
| **`secrets`** | values fetched by ARN when the task starts, given as environment variables |
| **execution role** | used by ECS before your code starts: pull images, write logs, fetch secrets |
| **task role** | used by your code while it runs |
| **`awsvpc`** | network mode: each task gets its own ENI, private IP and security groups |
| **target type `ip`** | what a target group for Fargate tasks must use |
| **`assignPublicIp=DISABLED`** | no public IP; tasks reach AWS via NAT or VPC endpoints |
| **rolling deployment** | replacing tasks a few at a time |
| **`minimumHealthyPercent`** / **`maximumPercent`** | the lowest and highest task counts during a rollout |
| **deployment circuit breaker** | marks a failing deployment `FAILED`; with rollback, returns to the last good revision |
| **blue/green**, **linear**, **canary** | deployments that shift traffic to the new revision in steps |
| **Application Auto Scaling** | scales ECS services and other things |
| **scalable target** | what is scaled: `service/CLUSTER/SERVICE`, dimension `ecs:service:DesiredCount` |
| **`ECSServiceAverageCPUUtilization`** | the service's average CPU |
| **Container Insights** | per-task and per-service CloudWatch metrics |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws ecs create-cluster --cluster-name apps --settings name=containerInsights,value=enabled` | creates a cluster |
| `aws ecs register-task-definition --cli-input-json file://...` | registers a revision |
| `aws ecs create-service --cluster C --service-name N --task-definition T --desired-count 2 --launch-type FARGATE --network-configuration ...` | creates a service |
| `awsvpcConfiguration={subnets=[A,B],securityGroups=[G],assignPublicIp=DISABLED}` | its network settings |
| `aws ecs update-service --cluster C --service N --deployment-configuration ...` | changes it in place |
| `deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200` | the deployment settings |
| `--force-new-deployment` | replaces tasks, for example to pick up a rotated secret |
| `aws application-autoscaling register-scalable-target --service-namespace ecs --resource-id service/C/N --scalable-dimension ecs:service:DesiredCount --min-capacity 2 --max-capacity 10` | makes it scalable |
| `aws application-autoscaling put-scaling-policy --policy-type TargetTrackingScaling ...` | adds target tracking |
| `aws ecs describe-services`, `describe-task-definition` | show what was made |
| `AmazonECSTaskExecutionRolePolicy` | managed policy: ECR pull and CloudWatch Logs |

### Errors

| Error | Means |
|---|---|
| `ClientException: No Fargate configuration exists for given values` | a CPU and memory pair Fargate does not offer |
| `CannotPullContainerError` | the image could not be pulled: wrong execution role, or no route to ECR |
| `ResourceInitializationError: unable to pull secrets or registry auth` | the execution role cannot read the secret, or there is no network path |

---

The previous lesson stored the `orders-api` image. Something now has to
**run** it: start copies of it, restart any that crash, spread them across
Availability Zones, roll out new versions without downtime, and add copies
when traffic grows. On a single server, you would do that by hand.
**Amazon ECS** (Elastic Container Service) is AWS's own scheduler for
containers, which does all of it. **Fargate** is the way to run ECS tasks
without servers: you never see or patch an EC2 instance; you choose CPU
and memory for each task and pay for exactly those, per second.

```text
 VPC 10.0.0.0/16
 ├── private-a (us-east-1a)    task 1: own ENI + private IP, security group orders-api
 └── private-b (us-east-1b)    task 2: own ENI + private IP, security group orders-api
       ▲
       │ cluster "apps" ─ service "orders-api" keeps 2 tasks running (2-10 with auto scaling)
       │                  each task = task definition "orders-api:1"
       │                     image  ECR orders-api:release-1   (pulled by the execution role)
       │                     logs   CloudWatch /ecs/orders-api (written by the execution role)
       │                     secret DB_PASSWORD from Secrets Manager (fetched by the execution role)
       │                     code   calls DynamoDB "orders"    (with the task role)
```

## Words first

| Term | What it is | Roughly like |
|---|---|---|
| **Cluster** | a named group of services and tasks; with Fargate, nothing more than a namespace | a folder |
| **Task definition** | a versioned **recipe**: image, CPU, memory, ports, environment, secrets, logging, roles. Each change registers a new **revision** (`orders-api:1`, `:2`...) | a launch template (Compute lesson 1) |
| **Task** | one running copy of a task definition: one or more containers started together | one instance |
| **Service** | keeps N tasks running, replaces failed ones, registers them with a load balancer, rolls out new revisions | an Auto Scaling group |

A task that runs once and ends (a nightly job) is started with `run-task`;
a long-running application is a **service**.

### Fargate or EC2?

| | **Fargate** | **ECS on EC2** |
|---|---|---|
| Servers | none to manage | your instances in the cluster, which you patch and scale |
| You pay for | each task's CPU and memory, per second | the instances, whether full or empty |
| Good for | most services, spiky or small workloads | GPUs, special instance types, very large steady fleets packed densely |

## The task definition

**CPU and memory.** CPU is in units of 1/1024 vCPU (`512` is half a vCPU),
memory in MiB. Fargate allows only certain **combinations**:

| CPU | Memory |
|---|---|
| 256 (.25 vCPU) | 512, 1024, 2048 |
| 512 (.5 vCPU) | 1024 to 4096, in 1024 steps |
| 1024 (1 vCPU) | 2048 to 8192, in 1024 steps |
| 2048 (2 vCPU) | 4096 to 16384, in 1024 steps |
| 4096 (4 vCPU) | 8192 to 30720, in 1024 steps |

(8 and 16 vCPU exist too, with up to 60 and 120 GiB.) Asking for, say, 512
CPU with 512 MiB fails at registration in real AWS with
`ClientException: No Fargate configuration exists for given values`.

**Container definitions** list each container: its `image`,
`portMappings`, `environment` (plain values), `secrets`, and
`logConfiguration`. With the **`awslogs`** log driver, everything the
container writes to standard output goes to a CloudWatch log group:

```json
"logConfiguration": {"logDriver": "awslogs", "options": {
  "awslogs-group": "/ecs/orders-api", "awslogs-region": "us-east-1",
  "awslogs-stream-prefix": "orders-api"}}
```

**Secrets.** `environment` values are visible to anyone who can read the
task definition. A password goes in **`secrets`** instead, as a reference:

```json
"secrets": [{"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:prod/orders/db-AbCdEf"}]
```

ECS fetches the value **when the task starts** and hands it to the
container as the environment variable `DB_PASSWORD`; the task definition
only ever holds the ARN. `valueFrom` can also be a Parameter Store
parameter (Security lesson 2). ❗ Because the value is read at start-up, a
rotated password reaches running tasks only when they are replaced (a new
deployment, `update-service --force-new-deployment`).

## Two roles, two jobs

A task definition names two IAM roles, both trusted by
`ecs-tasks.amazonaws.com`. Mixing them up is the classic ECS mistake:

| | **Execution role** | **Task role** |
|---|---|---|
| Used by | ECS itself, **before** your code starts | **your application code**, while it runs |
| For | pulling the image from ECR, creating log streams, fetching `secrets` | whatever the application calls: DynamoDB, S3, SQS |
| Typical policy | `AmazonECSTaskExecutionRolePolicy` (ECR pull, CloudWatch Logs), plus `secretsmanager:GetSecretValue` for its secrets | the least privilege the application needs |
| If it is wrong | the task never starts: `CannotPullContainerError`, or `ResourceInitializationError: unable to pull secrets or registry auth` | the task runs, and the application's calls fail with `AccessDenied` |

The SDK inside the container finds the task role's credentials by itself,
the way code on EC2 finds the instance profile's (Foundations lesson 8). The
application should not be able to pull arbitrary images, and ECS does not
need your table, so each role gets only its own job.

## Networking: awsvpc

Fargate tasks always use **`awsvpc`** networking: each task gets its **own
network interface** (ENI) and private IP address in your subnets, and its
own **security groups**, exactly like an instance. Consequences:

- Security group rules apply per task; this lesson's allows port 8080 from
  inside the VPC only.
- A load balancer's target group for Fargate tasks must have the target
  type **`ip`**, not `instance`.
- Tasks belong in **private subnets** with `assignPublicIp=DISABLED`. They
  still need to reach ECR, CloudWatch Logs and Secrets Manager, through a
  NAT gateway (Networking lesson 1) or VPC endpoints: `ecr.api`, `ecr.dkr`,
  the **S3 gateway** endpoint (image layers live in S3), `logs` and
  `secretsmanager`. Without either, tasks fail to start with
  `CannotPullContainerError`.

## Deployments that undo themselves

Changing the task definition and updating the service starts a **rolling
deployment**, bounded by two percentages of the desired count:

| `minimumHealthyPercent` / `maximumPercent` | With 2 tasks | Effect |
|---|---|---|
| **100 / 200** | starts 2 new tasks, then stops the 2 old ones | capacity never drops; briefly costs double |
| 50 / 100 | stops 1 old, starts 1 new, and so on | no extra cost; half the capacity during the rollout |

If the new revision is broken (a crash at start-up, failing health checks),
a plain rolling deployment keeps trying forever. The **deployment circuit
breaker** watches it: after repeated failures it marks the deployment
`FAILED` and, with **`rollback`** on, goes back to the last revision that
worked. Always turn it on. ECS also has built-in **blue/green**, **linear**
and **canary** deployments, which shift load balancer traffic to the new
revision in steps; section 9 covers CodeDeploy, the older way to do the same.

## Scaling

Services scale through **Application Auto Scaling**, a separate service
that scales many things (ECS services, DynamoDB capacity, Aurora replicas).
Two calls:

1. `register-scalable-target`: the service's desired count, written as
   resource ID `service/CLUSTER/SERVICE` and dimension
   `ecs:service:DesiredCount`, with a minimum and maximum;
2. `put-scaling-policy` with **target tracking** (Compute lesson 3): keep
   average CPU (`ECSServiceAverageCPUUtilization`), memory, or ALB requests
   per target at a value. Application Auto Scaling creates the CloudWatch
   alarms itself.

**Container Insights**, a cluster setting, adds CloudWatch metrics per
task and service (CPU, memory, network, restarts). 💸 Its metrics are
billed as custom metrics.

## Your task

Done for you: the foundations VPC (`awslab given vpc`, subnets `private-a`
and `private-b`), and a secret `prod/orders/db`.

1. A log group **`/ecs/orders-api`** with **30 days** retention.
2. Two roles trusted by `ecs-tasks.amazonaws.com`:
   - **`orders-api-execution`** with the managed policy
     `AmazonECSTaskExecutionRolePolicy`;
   - **`orders-api-task`** with an inline policy allowing
     `dynamodb:GetItem`, `PutItem`, `UpdateItem` and `Query` on the table
     **`orders`** only. The check also confirms it cannot delete the table,
     read other tables, or pull images (`ecr:BatchGetImage`).
3. A cluster **`apps`** with **Container Insights** enabled.
4. A task definition **`orders-api`** for **Fargate** (`requiresCompatibilities`
   `FARGATE`), network mode `awsvpc`, **512** CPU and **1024** MiB, with
   both roles set; one container named **`orders-api`**:
   - image `ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-1`
     (your account's ID);
   - port **8080**;
   - the `awslogs` driver to `/ecs/orders-api`;
   - the secret's ARN injected as **`DB_PASSWORD`** through `secrets`, and
     not also as a plain `environment` variable.
5. A security group **`orders-api`** in the VPC allowing TCP **8080** from
   `10.0.0.0/16`, and nothing from `0.0.0.0/0`.
6. A service **`orders-api`** in `apps`: **2** tasks, launch type
   **Fargate**, in the subnets **`private-a`** and **`private-b`**, with the
   security group above and **no public IP**.
7. Then change the service in place, as you would one already running:
   `update-service` with the circuit breaker **enabled with rollback**,
   minimum healthy **100%** and maximum **200%**. (In real projects set
   these at creation; the emulator keeps them only from an update.)
8. Auto scaling from **2** to **10** tasks, with a target tracking policy on
   average CPU (`ECSServiceAverageCPUUtilization`) at **60**.

After **Run**:

```
$ aws ecs describe-services --cluster apps --services orders-api \
    --query 'services[0].[desiredCount,runningCount,launchType,deploymentConfiguration]'
[
    2,
    0,
    "FARGATE",
    {
        "deploymentCircuitBreaker": {
            "enable": true,
            "rollback": true
        },
        "maximumPercent": 200,
        "minimumHealthyPercent": 100
    }
]
```

`runningCount` is 0 because the emulator records the service but runs no
containers; in AWS it would reach 2 once both tasks pass their checks.
`aws ecs describe-task-definition --task-definition orders-api --query
'taskDefinition.[family,revision,cpu,memory]' --output text` prints
`orders-api 1 512 1024`: registering again would make revision 2.

## Check yourself

1. Tasks stay in `PENDING` and then stop with `CannotPullContainerError`.
   Which role, or what network path, do you check?
   *The execution role (ECR pull permissions), and the route to ECR from
   the private subnets: a NAT gateway, or the ECR and S3 endpoints.*
2. The application logs `AccessDenied` calling DynamoDB. Which role?
   *The task role.*
3. Why `secrets` and not `environment` for `DB_PASSWORD`?
   *`environment` values are stored in the task definition, readable by
   anyone who can describe it; `secrets` stores only the ARN.*
4. A deployment of a broken image starts. What does the circuit breaker
   with rollback do?
   *Marks the deployment failed after repeated task failures, and returns
   the service to the last working revision.*
5. Why must an ALB target group for Fargate use target type `ip`?
   *With awsvpc each task has its own IP; there is no instance to register.*
