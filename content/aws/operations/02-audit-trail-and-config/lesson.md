---
title: An audit trail and config rules
summary: Who did what, and is it still compliant - a multi-Region CloudTrail trail with log file validation into a bucket only CloudTrail can write to, and AWS Config recording resources and checking them against rules.
order: 2
files: [setup.sh, trail-bucket-policy.json]
run: awslab run setup.sh
hints:
  - "The trail bucket's policy has two statements for `\"Principal\": {\"Service\": \"cloudtrail.amazonaws.com\"}`: `s3:GetBucketAcl` on the bucket, and `s3:PutObject` on `arn:aws:s3:::lb-audit-trail/AWSLogs/123456789012/*` with `\"Condition\": {\"StringEquals\": {\"s3:x-amz-acl\": \"bucket-owner-full-control\"}}`."
  - "`aws cloudtrail create-trail --name org-trail --s3-bucket-name lb-audit-trail --is-multi-region-trail --enable-log-file-validation`, then `aws cloudtrail start-logging --name org-trail` - a new trail does not log until started."
  - "Config needs a recorder and a delivery channel: `aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=\"$CONFIG_ROLE\" --recording-group allSupported=true,includeGlobalResourceTypes=true`, `aws configservice put-delivery-channel --delivery-channel name=default,s3BucketName=lb-audit-config`, `aws configservice start-configuration-recorder --configuration-recorder-name default`."
  - "A managed rule: `aws configservice put-config-rule --config-rule '{\"ConfigRuleName\":\"s3-versioning\",\"Source\":{\"Owner\":\"AWS\",\"SourceIdentifier\":\"S3_BUCKET_VERSIONING_ENABLED\"}}'`."
---

## CloudTrail: who did what

Every AWS API call - console, CLI, SDK, or AWS itself acting for you - is
an **event**: who, what, when, from where, and whether it worked.
**CloudTrail** keeps the last 90 days of management events in its **event
history** for free. A **trail** delivers events to S3 (and optionally
CloudWatch Logs) for as long as you keep them:

- **Multi-Region**: one trail captures every Region - including Regions
  nobody is supposed to use, which is exactly where an intruder would.
- **Log file validation**: CloudTrail writes signed digest files, so you can
  prove later that no log file was altered or deleted.
- An **organization trail** in the management account covers every account.
- **Management events** (create, delete, change) are on by default; **data
  events** (every S3 object read, every Lambda invoke) are opt-in and billed.

The bucket must let CloudTrail write - and nobody else should be able to.

## Config: is it still how it should be?

CloudTrail records actions; **AWS Config** records **state**. It takes a
**configuration item** every time a supported resource changes, so you can
see what a security group looked like last Tuesday. **Config rules** check
resources against a desired state - **AWS managed rules** like
`S3_BUCKET_VERSIONING_ENABLED` or `ENCRYPTED_VOLUMES`, or your own in
Lambda - and mark them compliant or not. Rules can trigger **automatic
remediation** through Systems Manager documents. **Conformance packs**
bundle rules for a standard.

Config needs a **configuration recorder** (with a role) and a **delivery
channel** (an S3 bucket) before it records anything.

| Question | Service |
|---|---|
| Who deleted the database? | CloudTrail |
| Was this bucket ever public, and when did that change? | Config |
| Is anyone attacking us? | GuardDuty |

## Your task

The script creates the buckets **`lb-audit-trail`** and
**`lb-audit-config`** and a role for Config. Add:

1. **`trail-bucket-policy.json`**: CloudTrail may read the bucket ACL and
   write objects under `AWSLogs/123456789012/` with the
   `bucket-owner-full-control` ACL - and apply it to `lb-audit-trail`;
2. a trail **`org-trail`**: **multi-Region**, **log file validation** on,
   into `lb-audit-trail`, **started**;
3. a Config **recorder** named `default` recording **all supported**
   resources **including global ones**, a **delivery channel** to
   `lb-audit-config`, and the recorder **started**;
4. the managed rules **`s3-versioning`** (`S3_BUCKET_VERSIONING_ENABLED`) and
   **`ebs-encrypted`** (`ENCRYPTED_VOLUMES`).
