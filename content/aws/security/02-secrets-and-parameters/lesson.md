---
title: Secrets Manager and Parameter Store
summary: A database secret with a generated password, its own KMS key, a resource policy and 30-day rotation; configuration in a Parameter Store hierarchy; and an application role that can read exactly its own settings.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`PASSWORD=$(aws secretsmanager get-random-password --password-length 32 --exclude-punctuation --query RandomPassword --output text)`, then build the JSON with python3 or printf so the quoting stays sane."
  - "`aws secretsmanager create-secret --name prod/orders/db --kms-key-id alias/app --secret-string file://db-secret.json --tags Key=env,Value=prod`."
  - "`aws secretsmanager rotate-secret --secret-id prod/orders/db --rotation-lambda-arn \"$ROTATE_ARN\" --rotation-rules AutomaticallyAfterDays=30 --no-rotate-immediately`."
  - "The resource policy denies `secretsmanager:GetSecretValue` to `\"Principal\": \"*\"` with `\"Condition\": {\"StringNotEquals\": {\"aws:PrincipalArn\": \"<orders-app ARN>\"}}`; set it with `aws secretsmanager put-resource-policy --secret-id prod/orders/db --resource-policy file://secret-policy.json`."
  - "`aws ssm put-parameter --name /orders/prod/api_key --type SecureString --key-id alias/app --value ...`. GetParametersByPath is authorized on the path itself, so the role needs both `parameter/orders/prod` and `parameter/orders/prod/*`."
---

Credentials and configuration do not belong in code, images or environment
files. AWS has two services for them, and they overlap.

## Which one

| | **Secrets Manager** | **Parameter Store** (Systems Manager) |
|---|---|---|
| For | credentials, API keys | configuration, and secrets that do not rotate |
| Rotation | built in, through a Lambda function (managed for RDS, Redshift, DocumentDB) | none - write your own |
| Encryption | always, with KMS | `SecureString` only |
| Size | 64 KB | 4 KB standard, 8 KB advanced |
| Cost | per secret per month, plus API calls | standard parameters are free |
| Cross-account | resource policies | sharing advanced parameters only |

Both are fetched at run time by a role, so nothing secret is stored with
the application. ECS, Lambda and CloudFormation can reference either one
directly.

## Rotation without downtime

A rotation function runs four steps - **createSecret**, **setSecret**,
**testSecret**, **finishSecret** - and moves the staging labels:
`AWSPENDING` on the new version while it is tested, then `AWSCURRENT`, with
the old one kept as `AWSPREVIOUS`. Applications that always ask for
`AWSCURRENT` (the default) pick up the new password without a deploy. The
**alternating users** strategy keeps two database users and switches
between them, so there is never a moment when the current password does not
work.

## A resource policy as a second lock

A secret can carry a **resource policy**. A deny with
`StringNotEquals aws:PrincipalArn` means that even an administrator with
`secretsmanager:*` in IAM cannot read the value - only the named
application role can. (Deny statements like this need care: a typo locks
everyone out until the policy is changed.)

## Hierarchies in Parameter Store

Name parameters like paths - `/orders/prod/db_host`, `/orders/dev/db_host` -
and an application reads its whole branch with one `GetParametersByPath`
call, while IAM policies grant per branch. Types are `String`, `StringList`
(comma-separated) and `SecureString` (encrypted with a KMS key you choose).

## Your task

Done for you: the key **`alias/app`**, and a rotation function
**`rotate-db`** (the emulator stores it but never runs it).

1. A secret **`prod/orders/db`**, encrypted with `alias/app`, tagged
   `env=prod`, whose value is JSON with `username` **`orders`** and a
   **32-character** password **generated** by Secrets Manager with no
   punctuation.
2. Rotation of that secret every **30 days** with `rotate-db`, without
   rotating immediately.
3. A role **`orders-app`** trusted by `ecs-tasks.amazonaws.com`, and a
   resource policy on the secret that **denies** `GetSecretValue` to every
   principal **except** `orders-app`.
4. Parameters **`/orders/prod/db_host`** (`String`, `orders.db.internal`),
   **`/orders/prod/allowed_origins`** (`StringList`,
   `https://shop.example.com,https://admin.example.com`) and
   **`/orders/prod/api_key`** (`SecureString` with `alias/app`, any value).
5. An inline policy **`read-config`** on `orders-app` that allows exactly:
   `ssm:GetParametersByPath` and `ssm:GetParameters` on the `/orders/prod`
   branch, `secretsmanager:GetSecretValue` on the secret's ARN, and
   `kms:Decrypt` on the `alias/app` key's ARN - no wildcard actions.

After **Run**: `aws ssm get-parameters-by-path --path /orders/prod
--with-decryption`.
