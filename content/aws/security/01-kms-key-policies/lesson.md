---
title: KMS key policies and envelope encryption
summary: A customer managed key whose policy separates the people who manage it from the code that uses it, encryption context as a condition, a grant, a data key for envelope encryption, and a multi-Region key with a replica.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "Your account ID: `ACCOUNT=$(aws sts get-caller-identity --query Account --output text)`. Role ARNs are then `arn:aws:iam::$ACCOUNT:role/<name>`."
  - "Write the key policy with python3 (as the SQS lesson does) and pass it as `--policy file://key-policy.json`. Then `aws kms create-key --description \"orders data\" --policy file://key-policy.json`."
  - "The usage statement's condition: `\"Condition\": {\"StringEquals\": {\"kms:EncryptionContext:app\": \"orders\"}}`."
  - "`aws kms create-grant --key-id \"$KEY_ID\" --grantee-principal \"$REPORTING_ARN\" --operations Decrypt --constraints EncryptionContextSubset={app=orders} --name reporting-read`."
  - "Envelope encryption: `aws kms generate-data-key --key-id alias/orders --key-spec AES_256 --encryption-context app=orders --query CiphertextBlob --output text | base64 -d > orders.key.enc`."
  - "Multi-Region is chosen at creation: `aws kms create-key --multi-region --description \"orders global\" --policy file://key-policy.json`, then `aws kms replicate-key --key-id \"$GLOBAL_ID\" --replica-region eu-west-1`."
---

Lesson 6 of the foundations made a key and let S3 use it. This one is about
**who** may use a key, and how applications really encrypt data with it.

## The key policy is the front door

Every KMS key has exactly one **key policy**, and unlike most resources, IAM
alone is not enough: a principal can use a key only if the key policy
allows it, directly or by delegating to IAM. The usual first statement
delegates to the account:

```json
{"Sid": "EnableIAM", "Effect": "Allow",
 "Principal": {"AWS": "arn:aws:iam::ACCOUNT:root"},
 "Action": "kms:*", "Resource": "*"}
```

It means "IAM policies in this account may grant access to this key" - it
does **not** give the root user special treatment. Remove it, and only the
principals named in the key policy can ever use the key (lock yourself out
and only AWS Support can help).

Then **separate duties**:

| Who | Gets | Never gets |
|---|---|---|
| Key administrators | `kms:Create*`, `Describe*`, `Enable*`, `List*`, `Put*`, `Update*`, `Revoke*`, `Disable*`, `Get*`, `Delete*`, `TagResource`, `UntagResource`, `ScheduleKeyDeletion`, `CancelKeyDeletion` | `Encrypt`, `Decrypt`, `GenerateDataKey*` |
| Key users (applications) | `Encrypt`, `Decrypt`, `ReEncrypt*`, `GenerateDataKey*`, `DescribeKey` | anything that changes the key |

The people who can delete a key cannot read the data, and the code that
reads the data cannot delete the key.

## Encryption context

An **encryption context** is a set of key-value pairs bound to a ciphertext:
the same pairs must be supplied to decrypt it. It is not secret, it is
logged in CloudTrail, and it can be a **condition**:
`kms:EncryptionContext:app = orders` lets the application use the key only
for its own data.

## Grants

A **grant** gives one principal specific operations on one key, without
editing the key policy - AWS services use them all the time (EBS, RDS). A
grant can carry constraints, such as an encryption context subset, and is
revoked with `revoke-grant` or `retire-grant`.

## Envelope encryption

KMS encrypts at most 4 KB directly. For real data, ask KMS for a **data
key**: `GenerateDataKey` returns it twice - in plaintext, to encrypt the
data locally and then discard, and encrypted under the KMS key, to store
next to the data. To read, send the encrypted data key to `Decrypt`, get
the plaintext key back, decrypt locally. Only small keys ever travel to KMS,
and every decrypt is an authorized, logged API call.

## Multi-Region keys

A **multi-Region key** (`mrk-...` ID) has replicas in other Regions with the
same key material, so data encrypted in one Region can be decrypted in
another without calling across Regions - useful for replicated data and
disaster recovery. Each replica has its own key policy.

## Your task

1. Two roles trusted by `ec2.amazonaws.com`: **`orders-app`** and
   **`reporting`**. A role **`key-admin`** trusted by your account
   (`arn:aws:iam::ACCOUNT:root`).
2. A customer managed key, described as "orders data",
   whose key policy has three statements: the account delegation above;
   **`key-admin`** with the administrator actions from the table and no
   cryptographic ones; **`orders-app`** with `kms:Encrypt`, `kms:Decrypt`,
   `kms:GenerateDataKey*` and `kms:DescribeKey` only when the encryption
   context `app` is `orders`.
3. The alias **`alias/orders`**, and automatic rotation on.
4. A grant named **`reporting-read`** giving **`reporting`** only
   `Decrypt`, constrained to the encryption context `app=orders`.
5. A data key from `alias/orders` (AES_256, context `app=orders`), with its
   **encrypted** copy saved, raw bytes, to **`orders.key.enc`**.
6. A second key, **multi-Region**, described as "orders global", with the
   same key policy and the alias **`alias/orders-global`**, and a replica of
   it in **eu-west-1**.

After **Run**, `aws kms get-key-policy --key-id alias/orders --policy-name
default --output text` shows the policy you wrote.
