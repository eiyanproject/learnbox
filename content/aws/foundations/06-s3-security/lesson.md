---
title: Locking down a bucket
summary: Block Public Access, default encryption with your own KMS key, key rotation, and a bucket policy that refuses anything not sent over TLS.
order: 6
files: [setup.sh, bucket-policy.json]
run: awslab run setup.sh
hints:
  - "All four Block Public Access settings in one call: `--public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true`."
  - "`aws kms create-key --description ... --query KeyMetadata.KeyId --output text` prints the new key's ID; keep it in a variable. Then `aws kms create-alias --alias-name alias/lb-data --target-key-id \"$KEY_ID\"` and `aws kms enable-key-rotation --key-id \"$KEY_ID\"`."
  - "Default encryption: `aws s3api put-bucket-encryption --bucket lb-data --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\",\"KMSMasterKeyID\":\"alias/lb-data\"},\"BucketKeyEnabled\":true}]}'`."
  - "The bucket policy denies `s3:*` to `\"Principal\": \"*\"` on both the bucket and its objects - `arn:aws:s3:::lb-data` and `arn:aws:s3:::lb-data/*` - with `\"Condition\": {\"Bool\": {\"aws:SecureTransport\": \"false\"}}`. Apply it last: see the note at the end."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **public** (bucket) | readable by anyone on the internet |
| **ACL** | access control list: S3's oldest per-object grants; legacy, keep them off |
| **bucket policy** | a resource policy attached to the bucket |
| **resource policy** | a policy on a resource, with a `Principal` saying who it is about |
| **Block Public Access** | four switches that override ACLs and policies that would make data public |
| **override** vs **edit** | Block Public Access ignores a public policy; the policy stays, and returns if the switch goes off |
| **at rest** | while stored on disk |
| **in transit** | while travelling over the network |
| **SSE-S3** | server-side encryption with keys S3 manages; the default since January 2023 |
| **SSE-KMS** | server-side encryption with a KMS key you control |
| **SSE-C** | you send your own key with every request; S3 keeps none |
| **client-side encryption** | encrypting before upload, so S3 only sees ciphertext |
| **ciphertext** | encrypted data |
| **KMS** | Key Management Service: stores and uses encryption keys |
| **KMS key** | a key in KMS; must be in the bucket's Region |
| **key policy** | the policy on a KMS key: who may use it |
| **default encryption** | how a bucket encrypts new objects; existing ones are unchanged |
| **key rotation** | new key material on a schedule (yearly by default); old data stays readable |
| **key material** | the secret bits a key encrypts with |
| **S3 Bucket Key** | a short-lived bucket-level key that cuts KMS requests by up to 99% |
| **alias** | a friendly name for a key, such as `alias/lb-data` |
| **TLS** | the encryption behind HTTPS |
| **HTTP** vs **HTTPS** | plain web traffic vs encrypted web traffic |
| **condition key** | a fact about the request a `Condition` tests, such as `aws:SecureTransport` |
| **`aws:SecureTransport`** | `true` for TLS requests, `false` otherwise |
| **`Bool`** | condition operator comparing a true/false key |
| **`"Principal": "*"`** | everyone, including your own account |
| **private by default** | a new bucket is accessible only to its own account |
| **Object Ownership** | "bucket owner enforced" turns ACLs off entirely |
| **role separation** | an S3 administrator still cannot read SSE-KMS data without the key |
| **CloudFront** | AWS's content delivery network, used to serve a private bucket publicly |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws s3api put-public-access-block --bucket B --public-access-block-configuration ...` | sets the four switches |
| `aws s3api get-public-access-block --bucket B` | shows them |
| `aws kms create-key --description D` | creates a KMS key |
| `aws kms create-alias --alias-name alias/N --target-key-id ID` | names the key |
| `aws kms enable-key-rotation --key-id ID` | turns on automatic rotation |
| `aws kms get-key-rotation-status --key-id ID` | shows it (needs the ID, not the alias) |
| `aws kms describe-key --key-id alias/N` | looks up a key, and its ID, by alias |
| `aws s3api put-bucket-encryption --bucket B --server-side-encryption-configuration ...` | sets default encryption |
| `aws s3api put-bucket-policy --bucket B --policy file://bucket-policy.json` | applies a bucket policy |
| `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets` | the four Block Public Access settings |

### Errors

| Error | Means |
|---|---|
| `An error occurred (403) when calling the PutObject operation: Forbidden` | S3's access denied; here, the TLS-only policy refusing plain HTTP |
| `upload failed` | `aws s3 cp` reporting that error |

---

Most S3 data leaks are not clever attacks. They are buckets someone made
public by accident, with a permissive setting copied from a tutorial, or
data read over an unencrypted connection. This lesson closes the usual
doors on one bucket, in three layers:

```text
 who can reach it        Block Public Access: never public, whatever a policy says
 how it is stored        encrypted at rest with your own KMS key, which rotates
 how it travels          a bucket policy refusing anything not sent over TLS
```

## Block Public Access

S3 has two older ways to grant access to a bucket: **ACLs** (access control
lists, per-object grants from S3's early days) and **bucket policies**
(below). Either can make data public, to anyone on the internet. **Block
Public Access** is four switches that override both:

| Setting | Effect |
|---|---|
| `BlockPublicAcls` | refuse new ACLs that grant public access |
| `IgnorePublicAcls` | ignore any public ACLs already there |
| `BlockPublicPolicy` | refuse a bucket policy that grants public access |
| `RestrictPublicBuckets` | limit an existing public policy to AWS services and this account |

The first two deal with ACLs, the last two with policies. Block Public
Access overrides; it does not edit: an existing public policy or ACL stays
in place, ignored, and takes effect again the moment the setting is turned
off. New buckets have
all four on, and they can also be set once for the whole account, which
then wins over any bucket's own setting. Turn them off only for a bucket
that really serves the public, and even then, a website is better served
through CloudFront with the bucket kept private (section 8).

## Encryption at rest

**At rest** means while stored on disk. Since 5 January 2023, every new
object in S3 is encrypted at rest, by default with keys S3 manages for you
(**SSE-S3**, server-side encryption with S3-managed keys). You never see those keys and cannot
control them. Choosing **SSE-KMS** instead uses a key in **KMS** (Key
Management Service) that you control:

| | SSE-S3 | SSE-KMS with your key |
|---|---|---|
| Who controls the key | S3 | you, through the key's **key policy** |
| Reading an object needs | permission on the bucket | permission on the bucket **and** on the key |
| Audit | none per use | every use of the key logged in CloudTrail |
| Rotation | handled by S3 | **automatic rotation** you switch on (yearly by default) |
| Cost | free | 💸 a monthly fee per key and a small charge per request to KMS |

The middle row is the main reason to choose it: a person or program that
somehow gets permission to read the bucket still cannot read the data
without the key. Rotation creates new key material on a schedule, while
data encrypted under the old material stays readable, so nothing needs
re-encrypting.

Two rules for SSE-KMS: the KMS key must be in the **same Region** as the
bucket, and a bucket's default encryption applies only to objects written
**after** it is set; existing objects keep whatever encryption they had
until they are copied.

An **S3 Bucket Key** makes S3 fetch a short-lived key from KMS for the bucket
instead of calling KMS for every object, which cuts the number of KMS
requests, and their cost, for busy buckets by up to 99%.

An **alias** (`alias/lb-data`) is a friendly name for a key. Code and
settings that refer to the alias keep working if the alias is later moved
to a new key.

### Capturing the key ID

`create-key` answers with the new key's details; its ID is needed by the
next two calls, so capture it, as with the policy ARN in lesson 3:

```
KEY_ID=$(aws kms create-key --description "lb-data bucket key" \
  --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/lb-data --target-key-id "$KEY_ID"
aws kms enable-key-rotation --key-id "$KEY_ID"
```

Run shows the assignment with the value filled in, which is handy for
seeing what the variable held:

```
$ KEY_ID=4ee75f66-68bd-4591-8f29-d58e79a3e40a
$ aws kms create-alias --alias-name alias/lb-data --target-key-id 4ee75f66-68bd-4591-8f29-d58e79a3e40a
```

## Encryption in transit

**In transit** means while travelling over the network. S3 accepts plain
HTTP as well as HTTPS, and over plain HTTP, anyone on the path between you
and AWS can read the data. A bucket policy can refuse every request that
did not come over **TLS** (the encryption behind HTTPS), using the condition
key `aws:SecureTransport`, which is `true` for TLS requests and `false`
otherwise:

```json
{
  "Sid": "DenyInsecureTransport",
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::lb-data", "arn:aws:s3:::lb-data/*"],
  "Condition": { "Bool": { "aws:SecureTransport": "false" } }
}
```

Read it as "**deny** **everyone** **every S3 action** on the bucket and its
objects, **when** the request was not over TLS". The parts that are new:

- A **bucket policy** is a **resource policy**: it is attached to the
  bucket, not to an identity, so it has a **`Principal`**, saying who the
  statement is about. `"*"` means everyone, including your own account's
  users and roles.
- It is a **Deny**, so it overrides any Allow anywhere (lesson 3).
- It lists **both** resources, the bucket and its objects, because S3
  actions act on one or the other (lesson 3 again). With only `lb-data/*`,
  bucket-level actions such as listing would still work over HTTP.
- `Bool` compares a true/false condition key. The policy document goes
  around this statement as usual (`Version`, `Statement` list), and is
  applied with `aws s3api put-bucket-policy --bucket lb-data --policy
  file://bucket-policy.json`.

## Who controls access, all together

S3 is **private by default**: a new bucket and its objects are accessible
only to the account that owns them. Access is then opened, or closed, by:

- **identity policies** on your users and roles (lesson 3);
- the **bucket policy**, a resource policy, which can also allow other
  accounts or the public;
- **ACLs**, an older per-object mechanism. They are **legacy**: new buckets
  have **Object Ownership** set to "bucket owner enforced", which turns
  ACLs off entirely, and they should stay off;
- **Block Public Access**, which overrides anything that would make the
  bucket public, but does not restrict your own account's principals.

Server-side encryption has a third variant, **SSE-C**, where you send your
own key with every request and S3 keeps none; and data can also be
encrypted **client-side** before it is uploaded, so S3 only ever sees
ciphertext. SSE-KMS's special strength is **role separation**: an S3
administrator with full S3 permissions still cannot read the data without
permission on the key.

## Your task

For the bucket `lb-data` (the script creates it):

1. turn on all four **Block Public Access** settings;
2. create a **KMS key** with the alias **`alias/lb-data`**, and turn on its
   **rotation**;
3. make **SSE-KMS with that key** the bucket's default encryption, with the
   **Bucket Key** enabled;
4. upload `report.csv` (the script makes it) to the bucket, as
   `report.csv`;
5. write **`bucket-policy.json`** with a statement denying **`s3:*`** to
   **everyone** (`"Principal": "*"`) on **both** `arn:aws:s3:::lb-data` and
   `arn:aws:s3:::lb-data/*` when `aws:SecureTransport` is `false`, and apply
   it, **last**.

**Why last?** The sandbox emulator speaks plain HTTP. Once the TLS-only
policy is on, it refuses your own uploads too, which is exactly what it is
for, and why the check tries an upload and expects it to fail. Try it after
**Run**:

```
$ aws s3 cp report.csv s3://lb-data/again.csv
upload failed: ./report.csv to s3://lb-data/again.csv An error occurred (403) when calling the PutObject operation: Forbidden
```

`403 Forbidden` is how S3 says "access denied". `aws s3api
get-public-access-block --bucket lb-data` shows the switches, and `aws kms
get-key-rotation-status --key-id "$KEY_ID"` the rotation (that call needs
the key ID, not the alias; `aws kms describe-key --key-id alias/lb-data`
looks the ID up).
(Bucket-level reads like those still work here, because the emulator only
enforces the policy on object requests; real S3 would refuse them too over
plain HTTP.)

## Check yourself

1. Block Public Access is on, and an old bucket policy allows `"Principal":
   "*"`. Is the bucket public?
   *No, as long as the setting stays on; the policy is ignored, not
   deleted.*
2. Why choose SSE-KMS with your own key over SSE-S3?
   *Reading then also needs permission on the key, every use is logged, and
   you control the key policy and rotation.*
3. A TLS-only bucket policy names only `arn:aws:s3:::lb-data/*`. What is
   still allowed over plain HTTP?
   *Bucket-level actions, such as listing the bucket.*
4. Who can read a brand-new bucket with no policies?
   *Only the owning account's principals that have IAM permission.*
