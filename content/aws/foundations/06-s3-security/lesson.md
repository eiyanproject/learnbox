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

Most S3 data leaks are not clever attacks. They are buckets someone made
public by accident. This lesson closes the usual doors.

## Block Public Access

**Block Public Access** is four switches that override any ACL or bucket
policy that would make data public:

| Setting | Effect |
|---|---|
| `BlockPublicAcls` | refuse new public ACLs |
| `IgnorePublicAcls` | ignore any public ACLs already there |
| `BlockPublicPolicy` | refuse a bucket policy that grants public access |
| `RestrictPublicBuckets` | limit an existing public policy to AWS services and this account |

New buckets have all four on, and they can also be set for the whole
account. Turn them off only for a bucket that really serves the public - and
even then, a website is better served through CloudFront with the bucket kept
private.

## Encryption at rest

Every new object in S3 is encrypted at rest, by default with keys S3 manages
(**SSE-S3**). Choosing **SSE-KMS** instead means a **KMS key** you control:

- a key policy decides who may use it - so reading the object needs
  permission on the key as well as on the bucket;
- every use is logged in CloudTrail;
- you can turn on **automatic rotation** (yearly by default) without
  re-encrypting anything;
- an **S3 Bucket Key** cuts the number of calls to KMS, and the cost, for
  busy buckets.

An **alias** (`alias/lb-data`) is a friendly name for a key, and can be
moved to a new key later without changing anything that uses it.

## Encryption in transit

S3 accepts plain HTTP as well as HTTPS. A bucket policy can refuse every
request that did not come over TLS, using the condition key
`aws:SecureTransport`:

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

A bucket policy is a **resource policy**: it is attached to the bucket, not
to an identity, so it has a `Principal` - who the statement is about.

## Your task

For the bucket `lb-data` (the script creates it):

1. turn on all four **Block Public Access** settings;
2. create a **KMS key** with the alias **`alias/lb-data`** and **rotation on**;
3. make **SSE-KMS with that key** the bucket's default encryption, with the
   **Bucket Key** enabled;
4. upload `report.csv` to the bucket (the script makes it);
5. write **`bucket-policy.json`** denying any request not over TLS, and apply
   it - **last**.

**Why last?** The sandbox speaks plain HTTP. Once the TLS-only policy is on,
it refuses your own uploads too - which is exactly what it is for. Try it
after **Run**: `aws s3 cp report.csv s3://lb-data/again.csv` fails with 403.
