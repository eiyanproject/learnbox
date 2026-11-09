---
title: Writing IAM policies
summary: The JSON behind every permission - Effect, Action, Resource - how AWS decides between allow and deny, and a least-privilege policy of your own.
order: 3
files: [setup.sh, policy.json]
run: awslab run setup.sh
hints:
  - "Listing a bucket and reading its objects are two different resources. `s3:ListBucket` acts on the bucket, `arn:aws:s3:::lb-reports`; `s3:GetObject` acts on objects, `arn:aws:s3:::lb-reports/*`. One statement each."
  - "An explicit Deny beats any Allow. A third statement with `\"Effect\": \"Deny\"`, `\"Action\": \"s3:GetObject\"` and `\"Resource\": \"arn:aws:s3:::lb-reports/private/*\"` keeps private/ out of reach even though the second statement allows everything in the bucket."
  - "`aws iam create-policy --policy-name reports-read --policy-document file://policy.json` - note the `file://`. The command prints the new policy's ARN, `arn:aws:iam::123456789012:policy/reports-read`."
  - "No `*` for actions or resources: the check reads the document and refuses `\"Action\": \"s3:*\"` or `\"Resource\": \"*\"` in an Allow."
---

Every permission in AWS is a **policy document**: JSON with a list of
statements.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReports",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::lb-reports/*"
    }
  ]
}
```

- **Version** is always `2012-10-17` - the policy language version, not a date
  you choose.
- **Effect** is `Allow` or `Deny`.
- **Action** is `service:Operation`; `*` and `?` work as wildcards, so
  `s3:Get*` is every S3 action starting with Get.
- **Resource** is one or more ARNs the statement applies to.
- **Sid** is an optional label. **Condition** (later lessons) narrows a
  statement further: only from this network, only with MFA, only over TLS.

## How AWS decides

For each request, AWS looks at every policy that applies:

1. Any matching statement with **Deny**? Then **denied** - an explicit deny
   always wins.
2. Otherwise, any matching **Allow**? Then **allowed**.
3. Otherwise **denied**. Nothing is allowed unless something allows it -
   the *implicit deny*.

So permissions only ever add up from nothing, and a Deny is the way to carve
an exception out of a broad Allow.

## Buckets are not objects

The classic trap. In S3, the bucket and the objects in it are different
resources with different ARNs:

| Action | Acts on | Resource ARN |
|---|---|---|
| `s3:ListBucket` | the bucket | `arn:aws:s3:::lb-reports` |
| `s3:GetObject`, `s3:PutObject` | objects | `arn:aws:s3:::lb-reports/*` |

A policy allowing `s3:ListBucket` on `arn:aws:s3:::lb-reports/*` allows
nothing at all - and the error you get will not tell you why.

## Least privilege

Grant exactly what the job needs and no more. `"Action": "s3:*"` with
`"Resource": "*"` works on day one and becomes a liability on day two.
Start narrow; widen when something real needs it.

## Your task

The analysts need to read reports from the bucket `lb-reports` - but not the
files under `private/`, and they must not be able to change anything.

1. Write **`policy.json`**: list the bucket `lb-reports`, read every object
   in it, and **explicitly deny** reading anything under `private/`.
2. In `setup.sh`, create it as a customer managed policy named
   **`reports-read`**, create a group **`analysts`** with it attached, and a
   user **`carol`** in that group. (The script already creates the bucket.)

The check reads your policy the way AWS would and asks: can carol list the
bucket? read `q1.csv`? read `private/salaries.csv`? write anything?
