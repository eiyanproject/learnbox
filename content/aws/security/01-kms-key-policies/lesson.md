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

Foundations lesson 6 created a KMS key and let S3 use it. Encrypting data
is only half of the story: the other half is **who** may use the key, and
who may change or delete it. An encrypted database is only as safe as its
key's permissions; if every administrator can also decrypt, the encryption
protects against little. This lesson builds a key for an orders application
whose permissions separate duties, and then uses it the way real
applications do, through **envelope encryption**.

## KMS in brief

**KMS** (Key Management Service) creates and stores encryption keys and
performs operations with them (encrypt, decrypt, generate data keys) through
API calls. The key material never leaves KMS in plain form: you never
download a KMS key, you ask KMS to use it. KMS keys are **Regional**: a key
in us-east-1 cannot decrypt anything in eu-west-1 (multi-Region keys, at
the end, are the exception).

Keys come in three kinds:

| Kind | Example | You control the policy? | Rotation | 💸 Cost |
|---|---|---|---|---|
| **AWS owned** | what SSE-S3 and DynamoDB use by default | no, and you never see it | AWS's business | free |
| **AWS managed** | `aws/s3`, `aws/rds`, created when a service first needs one | no | every year, automatically | free (requests billed) |
| **Customer managed** | this lesson's key | **yes** | you choose (yearly by default, 90 to 2,560 days) | $1 a month per key, plus requests |

Only a customer managed key lets you write its policy, share it with
another account, or schedule its deletion, which is why this lesson creates
one. KMS **symmetric** keys (one secret key for both directions, the default)
are what AWS services use; **asymmetric** key pairs are for signing, or for
encryption by parties outside AWS with the public half.

## The key policy is the front door

Every KMS key has exactly one **key policy**, a resource policy like a bucket
policy. KMS is unusual: **IAM alone is not enough**. A principal can use a
key only if the key policy allows it, either directly or by delegating to
IAM. The usual first statement does the delegating:

```json
{"Sid": "EnableIAM", "Effect": "Allow",
 "Principal": {"AWS": "arn:aws:iam::ACCOUNT:root"},
 "Action": "kms:*", "Resource": "*"}
```

It means "IAM policies in this account may grant access to this key". It
does **not** give the root user special treatment; `root` here stands for
the account (Foundations lesson 4). In a key policy, `"Resource": "*"` means
"this key". ❗ Leave this statement out, and only the principals named in the
key policy can ever use or manage the key; name nobody who can manage it,
and the key is locked for good, with only AWS Support able to help.

Then **separate duties**:

| Who | Gets | Never gets |
|---|---|---|
| Key administrators | `kms:Create*`, `Describe*`, `Enable*`, `List*`, `Put*`, `Update*`, `Revoke*`, `Disable*`, `Get*`, `Delete*`, `TagResource`, `UntagResource`, `ScheduleKeyDeletion`, `CancelKeyDeletion` | `Encrypt`, `Decrypt`, `GenerateDataKey*` |
| Key users (applications) | `Encrypt`, `Decrypt`, `ReEncrypt*`, `GenerateDataKey*`, `DescribeKey` | anything that changes the key |

The people who can delete a key cannot read the data, and the code that
reads the data cannot delete the key. (Administrators can still edit the key
policy, and so could grant themselves more; CloudTrail records every such
change, which is the backstop.)

## Encryption context

An **encryption context** is a set of key-value pairs, such as `app=orders`,
supplied when data is encrypted. It is bound to the ciphertext: decrypting
requires the **same** pairs, or KMS refuses:

```
$ aws kms decrypt --ciphertext-blob fileb://orders.key.enc --encryption-context app=billing
An error occurred (InvalidCiphertextException) when calling the Decrypt operation:
```

The context is not secret: it is written in CloudTrail with every call,
which makes logs readable ("orders data was decrypted"). And it can be a
**condition** in the key policy: `kms:EncryptionContext:app = orders` lets
the application use the key only for its own data, never for billing's.

## Grants

A **grant** gives one principal specific operations on one key, without
editing the key policy. AWS services create them constantly: when EBS
attaches an encrypted volume, it grants itself what it needs, for as long as
it needs it. A grant only allows, never denies, can carry constraints (such
as "only with the encryption context `app=orders`"), and is removed with
`revoke-grant` (by a key administrator) or `retire-grant` (by the principal
named as retiring). Grants can take a few seconds to take effect.

## Envelope encryption

KMS's `Encrypt` call takes at most **4 KB** of data, and sending gigabytes
to KMS would be slow anyway. Real applications use **envelope encryption**:

```text
 encrypt:  GenerateDataKey(alias/orders) ──> data key, twice:
             plaintext copy  ──> encrypt the file locally, then forget it
             encrypted copy  ──> store next to the encrypted file
 decrypt:  Decrypt(encrypted copy) ──> plaintext data key ──> decrypt the file locally
```

1. Ask KMS for a **data key** with `GenerateDataKey`. It returns the same
   key twice: in **plaintext**, and **encrypted** under the KMS key.
2. Encrypt the data **locally** with the plaintext data key (any fast
   algorithm, such as AES-256), then discard the plaintext key from memory.
3. Store the **encrypted** data key next to the encrypted data. It is safe:
   only KMS can turn it back into the real key.
4. To read, send the encrypted data key to `Decrypt`, get the plaintext key
   back, and decrypt the data locally.

Only small keys ever travel to KMS, and every decryption is an authorized,
logged API call. S3, EBS and RDS do exactly this, with a data key per object
or volume.

```
$ aws kms generate-data-key --key-id alias/orders --key-spec AES_256 --encryption-context app=orders
{
    "CiphertextBlob": "Y2M5MDA2MmYtZmJhNC00MDVjLWJlNDct...",
    "Plaintext": "ZvyyfTWQIzGH9/FcZ1uzT6KE73sdrtEWrtLnWFSipvo=",
    "KeyId": "arn:aws:kms:us-east-1:123456789012:key/cc90062f-fba4-405c-be47-da64d8e83a35"
}
```

The CLI shows binary values **base64-encoded**: `Plaintext` is the 32-byte
(256-bit) key, as 44 base64 characters. To save the encrypted copy as raw
bytes, as the task asks, take only the `CiphertextBlob` and decode it:
`--query CiphertextBlob --output text | base64 -d > orders.key.enc`.
Reading it back needs `fileb://` (binary, Serverless lesson 3). `Decrypt`
needs no key ID: the ciphertext itself records which key made it.

## Multi-Region keys

A **multi-Region key** (its ID starts with `mrk-`) can have **replicas** in
other Regions with the **same key material** and ID, so data encrypted in
one Region can be decrypted in another without calling across Regions:
useful for data replicated between Regions, and for disaster recovery. It
must be created multi-Region from the start; an existing key cannot be
converted. Each replica is managed separately, with its own key policy.
Use them only where that is really needed, since a key that works in
several Regions is a wider blast radius.

## Your task

1. Two roles trusted by `ec2.amazonaws.com`, **`orders-app`** and
   **`reporting`**, and a role **`key-admin`** trusted by your account
   (`arn:aws:iam::ACCOUNT:root`, with your account's ID).
2. A customer managed key described as **"orders data"**, whose key policy
   has three statements:
   - the account delegation above;
   - **`key-admin`** with the administrator actions from the table, and no
     cryptographic ones (the check confirms it cannot encrypt or decrypt);
   - **`orders-app`** with `kms:Encrypt`, `kms:Decrypt`,
     `kms:GenerateDataKey*` and `kms:DescribeKey`, only when the encryption
     context `app` is `orders` (and nothing else: the check tries
     administrator actions too).
3. The alias **`alias/orders`** for it, and automatic rotation on.
4. A grant named **`reporting-read`** giving **`reporting`** only
   `Decrypt`, constrained to the encryption context `app=orders`.
5. A data key from `alias/orders` (AES_256, context `app=orders`), with only
   its **encrypted** copy saved, as raw bytes, to **`orders.key.enc`**. The
   check decrypts it with that context and expects a 256-bit key.
6. A second key, **multi-Region**, described as **"orders global"**, with
   the **same** key policy, the alias **`alias/orders-global`**, and a
   replica of it in **eu-west-1**.

After **Run**:

```
aws kms get-key-policy --key-id alias/orders --policy-name default --output text
aws kms list-grants --key-id alias/orders --query 'Grants[].[Name,Operations]'
aws kms decrypt --ciphertext-blob fileb://orders.key.enc --encryption-context app=orders --query KeyId
```

The last one works; drop `--encryption-context` and the same call fails
with `InvalidCiphertextException`. (Decrypting under a multi-Region key fails
in the emulator, which is why the task decrypts with the ordinary key.)

## Check yourself

1. Why does a KMS key need the `EnableIAM` statement?
   *Without it, IAM policies cannot grant access to the key, and only the
   principals named in the key policy can use it.*
2. Why do key administrators get no `Decrypt`?
   *So that the people who manage the key cannot read the data.*
3. Why not encrypt a 2 GB file directly with KMS?
   *`Encrypt` takes at most 4 KB; envelope encryption uses a data key
   locally instead.*
4. A ciphertext was encrypted with the context `app=orders`. What does a
   decrypt without it get?
   *`InvalidCiphertextException`.*
5. Does rotation re-encrypt old data?
   *No. Old ciphertexts stay decryptable with the old key material, which
   KMS keeps.*
