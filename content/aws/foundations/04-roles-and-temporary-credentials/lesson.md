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

A user has long-lived credentials: a password, maybe access keys. Leaked
keys are one of the commonest ways AWS accounts are broken into. A **role**
has no credentials of its own. Something trusted **assumes** it and gets
**temporary credentials** from STS - an access key, a secret and a session
token that expire on their own, by default after an hour.

Roles are how AWS wants nearly everything to get permissions:

- an **EC2 instance** or a **Lambda function** calling other AWS services;
- a person from **another account**, or signed in through Identity Center;
- you, **switching role** to do something risky with more permission than
  you normally carry.

## Two policies per role

| | Says | Attached as |
|---|---|---|
| **Trust policy** | *who* may assume the role | `--assume-role-policy-document` when the role is made |
| **Permissions policy** | *what* the role may do once assumed | `attach-role-policy`, like a user or group |

A trust policy names a **Principal** and allows `sts:AssumeRole`:

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

## Roles for EC2

Code on an instance should never carry access keys. Give the instance a
role instead: the SDKs and the CLI on it find the temporary credentials by
themselves, through the instance metadata service, and they rotate
automatically. An instance holds a role through an **instance profile** - a
container for exactly one role. (The console makes the profile for you
quietly; the CLI makes you do it.)

## Cross-account roles and the external ID

To let a partner's account in - an auditor, say - trust their account in the
role, and they assume it from their side. When the partner is a third party
acting for many customers, add an **external ID**: a value you agree with them
that must be presented when assuming the role. It stops someone else tricking
the partner into using *your* role for *their* purposes (the "confused
deputy").

```
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/auditor \
  --role-session-name check --external-id lb-audit-2026
```

returns `Credentials` - `AccessKeyId`, `SecretAccessKey`, `SessionToken`,
`Expiration` - and the session's identity, an `assumed-role` ARN.

## Your task

1. Write **`ec2-trust.json`** so that EC2 may assume the role, and in
   `setup.sh` create a role **`web-server`** from it with the AWS managed
   policy **`AmazonS3ReadOnlyAccess`** attached, and an instance profile, also
   named **`web-server`**, containing it.
2. Write **`auditor-trust.json`** so that account **`111122223333`** may assume
   it, but only with the external ID **`lb-audit-2026`**. Create a role
   **`auditor`** from it with the AWS managed policy **`SecurityAudit`**.

After **Run**, try assuming the auditor role yourself with the command above.
(The emulator does not check trust policies when you do - a real account
would refuse you, because you are not account 111122223333.)
