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

Every application has values it needs that must not be in its code: the
database password, an API key for the payment provider, the database's host
name, which domains may call it. Put them in the code, a container image or
an environment file, and they spread to every copy, every log of a build,
and every developer's laptop; and changing a password means a redeploy.
AWS has two services for keeping them outside the application, fetched at
run time by the application's role. This lesson uses both, for an orders
service running on ECS:

```text
 orders-app (role, ECS task) ──GetSecretValue──> Secrets Manager: prod/orders/db  (rotates every 30 days)
                             ──GetParametersByPath /orders/prod──> Parameter Store: db_host, allowed_origins, api_key
                             ──kms:Decrypt──> key alias/app (both are encrypted with it)
```

## Which one

The two overlap, and the exam asks which to choose:

| | **Secrets Manager** | **Parameter Store** (part of Systems Manager) |
|---|---|---|
| Meant for | credentials and API keys | configuration, and secrets that do not rotate |
| **Rotation** | **built in**, through a Lambda function (and managed rotation for RDS, Redshift, DocumentDB) | none: write your own |
| Encryption | always, with KMS | only for the `SecureString` type |
| Size of a value | up to 64 KB | 4 KB (standard tier), 8 KB (advanced) |
| 💸 Cost | $0.40 per secret per month, plus API calls | standard parameters free; advanced $0.05 a month each |
| Sharing with other accounts | resource policies | advanced parameters only |
| Copies in other Regions | yes, replicas | no |

The rule of thumb: "**rotate**" or "**database password**" in a question
means Secrets Manager; configuration values and simple secrets, Parameter
Store. ECS task definitions, Lambda and CloudFormation can reference either
directly, so the value never appears in the template or task definition
itself.

## Secrets and generated passwords

A secret holds a value, usually a small JSON document such as
`{"username": "orders", "password": "..."}`, and has a name, typically
path-like (`prod/orders/db`). `get-random-password` generates a strong
password, so no person ever chooses or sees it:

```
PASSWORD=$(aws secretsmanager get-random-password --password-length 32 \
  --exclude-punctuation --query RandomPassword --output text)
```

`--exclude-punctuation` avoids characters that some database drivers and
shells mishandle. Build the JSON with `python3`'s `json` module (Serverless
lesson 1), so the password is quoted correctly whatever it contains, and
delete the temporary file afterwards.

## Rotation without downtime

**Rotation** replaces the password regularly, so a password that leaks is
only useful for a while. Secrets Manager runs a **rotation function**, a
Lambda function, which works in four steps:

1. **createSecret**: generate a new password, and store it as a new
   **version** of the secret, labelled `AWSPENDING`;
2. **setSecret**: change the password in the database itself;
3. **testSecret**: sign in with it, to prove it works;
4. **finishSecret**: move the label `AWSCURRENT` to the new version; the
   old one becomes `AWSPREVIOUS`.

Applications that always ask for `AWSCURRENT` (the default) pick up the new
password at their next read, without a deploy. The **alternating users**
strategy goes further: two database users take turns, so there is never a
moment when the password an application holds stops working.
`--no-rotate-immediately` sets the schedule without rotating right now.
(The emulator stores the schedule and labels, and never runs the function.)

## A resource policy as a second lock

A secret can carry a **resource policy**, a resource-based policy as in
Foundations lesson 3. A deny with a condition on `aws:PrincipalArn`, the ARN
of whoever is asking, works as a second lock:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "*",
  "Condition": {"StringNotEquals": {"aws:PrincipalArn": "arn:aws:iam::ACCOUNT:role/orders-app"}}
}
```

Read it as "deny reading the value to everyone **except** the role
`orders-app`". Since an explicit deny wins over any allow, even an
administrator with `secretsmanager:*` in IAM cannot read the password, only
the application role can. In a resource policy attached to a secret,
`"Resource": "*"` means "this secret". ❗ A deny like this needs care: a
typo in the ARN locks everyone out, the application included, until the
policy is changed. (The emulator stores the policy but does not enforce it,
so `get-secret-value` still works for you here; the check evaluates it.)

## Hierarchies in Parameter Store

Name parameters like paths: `/orders/prod/db_host`, `/orders/dev/db_host`.
Then an application reads its whole branch with one call, and IAM policies
grant access per branch:

```
$ aws ssm get-parameters-by-path --path /orders/prod --with-decryption \
    --query 'Parameters[].[Name,Type]' --output table
--------------------------------------------------
|               GetParametersByPath              |
+-------------------------------+----------------+
|  /orders/prod/db_host         |  String        |
|  /orders/prod/allowed_origins |  StringList    |
|  /orders/prod/api_key         |  SecureString  |
+-------------------------------+----------------+
```

The three types: `String`; `StringList`, a comma-separated list; and
`SecureString`, encrypted with a KMS key you choose. Reading a SecureString
without `--with-decryption` returns the encrypted text; with it, the caller
also needs `kms:Decrypt` on the key. Parameters keep a version history, and
AWS publishes **public parameters** too, such as the latest AMI IDs used in
Foundations lesson 8.

### The IAM resource for a path

A parameter's ARN is `arn:aws:ssm:REGION:ACCOUNT:parameter/orders/prod/db_host`
(the parameter's name, without its leading `/`, after `parameter/`).
`GetParametersByPath` is authorized on the **path itself**, while
`GetParameters` is authorized on each parameter, so a policy for the branch
needs two resources: `...:parameter/orders/prod` and
`...:parameter/orders/prod/*`.

## Your task

Done for you: the KMS key **`alias/app`** (its ARN in `KEY_ARN`), and a
rotation function **`rotate-db`** (in `ROTATE_ARN`). Add:

1. A secret **`prod/orders/db`**, encrypted with `alias/app`, tagged
   `env=prod`, whose value is JSON with `username` **`orders`** and a
   **32-character** password **generated** by Secrets Manager with no
   punctuation.
2. Rotation of that secret every **30 days** with `rotate-db`, without
   rotating immediately.
3. A role **`orders-app`** trusted by `ecs-tasks.amazonaws.com` (the
   principal for roles of ECS tasks), and a resource policy on the secret
   that **denies** `GetSecretValue` to every principal (`"Principal": "*"`)
   **except** `orders-app`.
4. Three parameters:
   - **`/orders/prod/db_host`**, a `String`: `orders.db.internal`;
   - **`/orders/prod/allowed_origins`**, a `StringList`:
     `https://shop.example.com,https://admin.example.com`;
   - **`/orders/prod/api_key`**, a `SecureString` encrypted with
     `alias/app`, any value.
5. An inline policy **`read-config`** on `orders-app` allowing exactly:
   - `ssm:GetParametersByPath` and `ssm:GetParameters` on the
     `/orders/prod` branch (both resources above), and nothing under
     `/orders/dev`;
   - `secretsmanager:GetSecretValue` on **this** secret's ARN;
   - `kms:Decrypt` on the `alias/app` key's ARN;
   - with no wildcard actions, and nothing that writes.

After **Run**:

```
aws ssm get-parameters-by-path --path /orders/prod --with-decryption
aws secretsmanager describe-secret --secret-id prod/orders/db \
  --query '[RotationEnabled,RotationRules.AutomaticallyAfterDays,VersionIdsToStages]'
```

The second shows the rotation schedule and each version's labels.

## Check yourself

1. A database password must change every 30 days without downtime. Which
   service?
   *Secrets Manager, with rotation.*
2. What do `AWSCURRENT`, `AWSPENDING` and `AWSPREVIOUS` mean?
   *The version applications use, the new one being tested, and the one
   just replaced.*
3. An administrator has `secretsmanager:*` in IAM. Can they read the
   secret?
   *No: the resource policy's explicit deny wins.*
4. Why does `read-config` need both `parameter/orders/prod` and
   `parameter/orders/prod/*`?
   *`GetParametersByPath` is authorized on the path itself, `GetParameters`
   on each parameter.*
5. Reading `/orders/prod/api_key` with `--with-decryption` fails with
   `AccessDenied`. What is missing?
   *`kms:Decrypt` on the key that encrypted it.*
