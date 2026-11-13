---
title: Roles and temporary credentials
summary: Permissions without passwords or keys - roles for EC2 instances and for another account, trust policies, and what assuming a role hands back.
order: 4
files: [setup.sh, ec2-trust.json, auditor-trust.json]
run: awslab run setup.sh
hints:
  - "A trust policy has a Principal and no Resource. For EC2: `\"Principal\": {\"Service\": \"ec2.amazonaws.com\"}`, `\"Action\": \"sts:AssumeRole\"`."
  - "For the other account: `\"Principal\": {\"AWS\": \"arn:aws:iam::111122223333:root\"}`. `root` here means the whole account - that account then decides which of its own people may use the role."
  - "The external ID goes in a Condition: `\"Condition\": {\"StringEquals\": {\"sts:ExternalId\": \"lb-audit-2026\"}}`."
  - "An instance cannot use a role directly - it uses an instance profile with the role in it. `aws iam create-instance-profile --instance-profile-name web-server`, then `aws iam add-role-to-instance-profile --instance-profile-name web-server --role-name web-server`."
---

A user has **long-lived credentials**: a password, and maybe access keys,
which stay valid until someone deletes them. Access keys copied into code, a
config file or a public repository are one of the commonest ways AWS
accounts are broken into, because whoever finds them can use them for months.

A **role** solves this. It is an identity with permissions, like a user, but
with **no credentials of its own**. Instead, something trusted **assumes**
the role, and gets **temporary credentials** from STS (the Security Token
Service): an access key, a secret key and a session token that stop working
by themselves, after one hour by default. A leaked temporary credential is
useless soon after.

Roles are how AWS wants nearly everything to get permissions:

- an **EC2 instance** (a virtual server) or a **Lambda function** calling
  other AWS services;
- a person from **another AWS account**, or one signed in through IAM
  Identity Center;
- you, **switching role** to do something risky with more permission than
  you normally carry, so the extra power is only there when you ask for it.

This lesson makes two roles: one for a web server, and one for an outside
auditor.

## Two policies per role

A role has two kinds of policy, answering two different questions:

| | Says | Set with |
|---|---|---|
| **Trust policy** | **who** may assume the role | `--assume-role-policy-document` when the role is created |
| **Permissions policy** | **what** the role may do once assumed | `attach-role-policy`, as for a user or group |

A trust policy is a policy document like last lesson's, with two
differences: it names a **Principal**, the "who", and it has **no
Resource**, because the resource is the role itself. The action is always
`sts:AssumeRole`:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

Read it as "allow **the EC2 service** to assume this role". The two kinds of
Principal used here:

- `{"Service": "ec2.amazonaws.com"}`: an AWS **service**, acting for your
  resources;
- `{"AWS": "arn:aws:iam::111122223333:root"}`: another **account**. `root`
  here means the whole account, not its root user: account 111122223333
  then decides, with its own IAM policies, which of its people may use the
  role.

(Real IAM refuses a trust policy that has a `Resource`, with
`MalformedPolicyDocument`. The emulator is more lenient, so leave it out
yourself.) A wildcard cannot be used inside a Principal's ARN either: you
trust named accounts, roles and services, never "anything matching".

## Roles for EC2

Code running on an instance should never carry access keys. Give the
instance a role instead: the AWS SDKs and the CLI on the instance find the
temporary credentials by themselves, through the **instance metadata
service** (a small web service only the instance can reach), and they are
renewed automatically before they expire. Nothing to store, nothing to
rotate, nothing to leak.

An instance holds a role through an **instance profile**: a container for
exactly one role, which is what you attach to the instance. The console
quietly makes the profile for you, with the same name as the role; the CLI
makes you do it:

```text
 instance  ──uses──>  instance profile web-server  ──contains──>  role web-server
                                                                      │
                                                    permissions: AmazonS3ReadOnlyAccess
```

## Cross-account roles and the external ID

To let a partner's account in, such as an auditing firm, trust their
account in the role's trust policy, and they assume it from their side.

When the partner is a third party working for many customers, add an
**external ID**: a value you agree with them, which they must present when
they assume the role. Without it, there is a trick called the **confused
deputy**: another of the partner's customers tells the partner "my account's
role is `arn:aws:iam::123456789012:role/auditor`", which is really *yours*,
and the partner, trusted by your role, unknowingly fetches your data for
them. With the external ID, the partner presents the ID agreed with *that*
customer, and your role refuses it.

The same trick works against roles that trust an AWS **service**: an S3
bucket or SNS topic in someone else's account could ask the service to act
on your role. For service principals, the guard is a condition on
`aws:SourceArn` or `aws:SourceAccount`, naming the resource or account the
service may act for; Serverless lesson 2 uses one.

The ID goes in a **Condition**, which only allows the statement when the
request matches:

```json
"Condition": {
  "StringEquals": { "sts:ExternalId": "lb-audit-2026" }
}
```

## What assuming a role hands back

```
$ aws sts assume-role --role-arn arn:aws:iam::123456789012:role/auditor \
    --role-session-name check --external-id lb-audit-2026
{
    "Credentials": {
        "AccessKeyId": "ASIARZPUZDIKIT5YNK6N",
        "SecretAccessKey": "3fzjaG+29Lli...",
        "SessionToken": "FQoGZXIvYXdzEBYa...",
        "Expiration": "2026-11-13T01:26:18.884125Z"
    },
    "AssumedRoleUser": {
        "AssumedRoleId": "AROARZPUZDIKIQDXVGDLO:check",
        "Arn": "arn:aws:sts::123456789012:assumed-role/auditor/check"
    }
}
```

(Shortened; the keys are random every time.) A session lasts one hour by
default; `--duration-seconds` asks for up to 12 hours, as far as the role's
**maximum session duration** allows. A session that assumes another role
from inside a role session (**role chaining**) is capped at one hour,
whatever is asked. The three `Credentials`
values together are the temporary credentials, valid until `Expiration`.
Temporary access keys start with `ASIA`; long-lived user keys start with
`AKIA`, which is a quick way to tell them apart in a log. The session's
identity is an **assumed-role** ARN: role `auditor`, session `check`, the
name you chose with `--role-session-name`, which shows up in audit logs so
you can tell who did what.

## Using the temporary credentials

The three values `assume-role` returns are used like any credentials, by
putting them in the standard environment variables:

```
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
aws sts get-caller-identity      # now: ...:assumed-role/auditor/check
```

Every command after that runs as the role, with the role's permissions, and
anything the role is not allowed gets `AccessDenied` (or
`UnauthorizedOperation` for EC2). Unset the variables to go back. The SDKs
and the CLI do this for you on EC2 (instance profiles), in Lambda, and with
named profiles that say `role_arn = ...` in `~/.aws/config`.

## Roles without stored keys, everywhere

The same idea covers the other places keys used to be stored:

- **CI/CD systems** such as GitHub Actions assume a role through **OIDC
  federation**: the CI system proves who it is with a signed token, and the
  role's trust policy names the identity provider and, in a condition, the
  repository and branch allowed (`"Principal": {"Federated": ...}`, action
  `sts:AssumeRoleWithWebIdentity`).
- **Break-glass access**: people normally hold read-only permissions, and
  assume a powerful role only in an emergency, which CloudTrail records.
- **Service-linked roles** are created and managed by AWS services
  themselves (`AWSServiceRoleForECS`); leave them alone.

## Your task

1. Write **`ec2-trust.json`** so that the EC2 service, and **nothing else**,
   may assume the role. In `setup.sh`, create a role **`web-server`** from
   it, attach the AWS managed policy **`AmazonS3ReadOnlyAccess`**
   (`arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess`), and create an
   instance profile, also named **`web-server`**, containing the role.
2. Write **`auditor-trust.json`** so that account **`111122223333`** may
   assume it, but only with the external ID **`lb-audit-2026`**: every Allow
   statement in it needs the condition. Create a role **`auditor`** from it
   with **exactly one** policy attached, the AWS managed policy
   **`SecurityAudit`** (`arn:aws:iam::aws:policy/SecurityAudit`).

After **Run**, try assuming the auditor role yourself with the command
above. The emulator does not check trust policies when you do; a real
account would refuse you with `AccessDenied`, because you are not account
111122223333.

## Check yourself

1. What are the two policies on every role?
   *The trust policy (who may assume it) and its permissions policies (what
   it may do).*
2. Why does an EC2 instance need an instance profile, not just a role?
   *An instance can only hold a role through an instance profile, a
   container for one role.*
3. A third-party auditor serves many customers. What stops another customer
   from tricking it into using your role?
   *An external ID that the auditor must present, agreed with you.*
4. How long do credentials from `assume-role` last by default, and what if
   they leak?
   *One hour; after that they are useless.*
5. How can GitHub Actions deploy to AWS without any stored key?
   *OIDC federation to a role whose trust policy names the repository and
   branch.*
