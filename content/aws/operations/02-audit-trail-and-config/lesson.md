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

Sooner or later someone asks a question about the past. The production
database was deleted on Saturday night: who did it, from where? An auditor
asks whether any bucket was ever public in the last year. A security review
asks whether every disk is encrypted, today, and was yesterday. Lesson 1's
metrics and logs say how the *application* is doing. Two other services
answer these questions about the *account*:

| Question | Service |
|---|---|
| Who did what, when, from where? ("who deleted the database?") | **CloudTrail**: a record of API calls |
| What did a resource look like at a given time, and is it as it should be? ("was this bucket ever public?") | **AWS Config**: a record of resource state, checked against rules |
| Is anyone attacking us right now? | **GuardDuty** (threat detection from the logs; not in this lesson) |
| How is the application performing? | **CloudWatch** (lesson 1) |

## CloudTrail: who did what

Every action in AWS is an API call (Foundations lesson 1), whether it comes
from the console, the CLI, an SDK, or AWS itself acting for you. CloudTrail
records each one as an **event**: who made the call (the identity's ARN), the
action, when, from which IP address, and whether it worked.

There are two ways to keep events:

- **Event history** is on for every account, free, with no setup: the last
  **90 days** of **management events**, searchable in the console or with
  `aws cloudtrail lookup-events`. It cannot be kept longer or sent anywhere.
- A **trail** delivers events to an **S3 bucket** (and optionally to
  CloudWatch Logs), for as long as you keep the files. That is what an
  audit needs.

Events come in kinds, and only one is recorded by default:

| Kind | Examples | Recorded by default |
|---|---|---|
| **Management events** | creating, changing or deleting resources: `CreateBucket`, `TerminateInstances`, `PutBucketPolicy` | **yes** |
| **Data events** | operations on the data inside resources: each S3 `GetObject` and `PutObject`, each Lambda invoke | **no**: opt-in per resource type, and 💸 billed per event (they can be enormous in number) |
| **Insights events** | unusual rates of API calls | no |

So a trail with default settings will show who deleted a bucket, but not who
read a file from it. ❗ If you need object-level audit, you must add data
events.

Three trail settings matter:

- **Multi-Region**: one trail records every Region. Without it, a Region
  nobody is supposed to use is unrecorded, which is exactly where an
  intruder would start crypto-mining.
- **Log file validation**: CloudTrail also writes a signed **digest file**
  every hour, holding a SHA-256 hash of each log file, so you can later
  prove that no log file was altered or deleted (`aws cloudtrail
  validate-logs`). Evidence that could have been edited is weak evidence.
- An **organization trail**, created in an Organization's management
  account, records every account in it (section 7).

A new trail does **not** log until you **start** it with `start-logging`; the
check tests that it is logging, not only that it exists.

### The bucket only CloudTrail can write to

CloudTrail writes into your bucket as an AWS service, so the bucket's
policy must let it, and should let nothing else. CloudTrail needs two
permissions, each its own statement:

1. `s3:GetBucketAcl` on the **bucket**: CloudTrail checks the bucket's
   access control list before writing;
2. `s3:PutObject` on **`AWSLogs/<account ID>/*`** only, the path where it
   writes this account's logs, with the condition that each object is
   written with the ACL `bucket-owner-full-control`, so the bucket owner
   always owns the log files:

```json
"Condition": { "StringEquals": { "s3:x-amz-acl": "bucket-owner-full-control" } }
```

Both statements name the Principal `{"Service": "cloudtrail.amazonaws.com"}`.
Nothing in the policy allows anyone else (`"Principal": "*"`) to do anything:
the check refuses that. (In a real account, AWS also recommends an
`aws:SourceArn` condition naming your trail's ARN, so that only *your* trail
can write here: the confused-deputy guard from Foundations lesson 4.)

## AWS Config: is it still how it should be?

CloudTrail records **actions**; AWS Config records **state**. Each time a
supported resource changes, Config writes a **configuration item**: the
whole configuration of that resource at that moment. Together they form a
**configuration history**, so you can see what a security group looked like
last Tuesday, and which change opened port 22.

**Config rules** check resources against a desired state, and mark each
resource `COMPLIANT` or `NON_COMPLIANT`:

- **AWS managed rules**, ready-made and named by an identifier, such as
  `S3_BUCKET_VERSIONING_ENABLED` (every bucket has versioning on) or
  `ENCRYPTED_VOLUMES` (every attached EBS volume is encrypted);
- **custom rules**, written as Lambda functions or in a policy language.

Rules are evaluated when a relevant resource changes, on a schedule, or
both. A non-compliant resource can trigger **automatic remediation** through
a Systems Manager Automation document (for example, turning versioning back
on). **Conformance packs** bundle many rules and remediations for a
standard, such as a benchmark.

Config records nothing until it has two things:

- a **configuration recorder**, saying what to record, with a role
  allowing Config to read your resources (the starter creates it, with the
  managed policy `AWS_ConfigRole`). By default it does **not** record
  **global** resource types such as IAM users, roles and policies, so IAM
  changes would go unseen: `includeGlobalResourceTypes=true` adds them;
- a **delivery channel**, saying where to send the history (an S3 bucket).

Then the recorder must be **started**, like the trail. Stopping it later
means changes, including deletions, go unrecorded and rule results go stale.

💸 Config is billed per configuration item recorded and per rule evaluation,
which adds up in busy accounts.

## Using the trail

- A trail writes compressed JSON files to the bucket, a few minutes after
  each call, under `AWSLogs/<account>/CloudTrail/<Region>/<date>/`.
  **Athena** can query them with SQL, which is how old events are searched
  after the 90 days of event history.
- Calls to **global** services (IAM, STS, CloudFront) are recorded in
  **us-east-1**: one more reason a trail should cover all Regions.
- Every API call is also an event in **EventBridge** (Serverless lesson 4),
  so a rule can react to one particular call within seconds, for example
  sending an alert whenever someone calls `DeleteTrail` or signs in as root.
- Config **detects**, it does not prevent: a non-compliant resource is
  reported (and possibly remediated) after it exists. Preventing a change in
  the first place is the job of IAM policies and SCPs.

## Your task

The script creates the buckets **`lb-audit-trail`** and **`lb-audit-config`**
and the role for Config (in `CONFIG_ROLE`). Add:

1. **`trail-bucket-policy.json`**: CloudTrail (`cloudtrail.amazonaws.com`)
   may `s3:GetBucketAcl` on `lb-audit-trail`, and `s3:PutObject` on
   `arn:aws:s3:::lb-audit-trail/AWSLogs/123456789012/*` only, with the
   `bucket-owner-full-control` ACL condition; nothing for anyone else.
   Apply it to `lb-audit-trail`.
2. A trail **`org-trail`**: **multi-Region**, **log file validation** on,
   delivering to `lb-audit-trail`, and **started**.
3. A Config **recorder** named `default`, using the role, recording **all
   supported** resource types **including global ones**; a **delivery
   channel** to `lb-audit-config`; and the recorder **started**.
4. The AWS managed rules **`s3-versioning`** (`S3_BUCKET_VERSIONING_ENABLED`)
   and **`ebs-encrypted`** (`ENCRYPTED_VOLUMES`), each with `"Owner": "AWS"`.

After **Run**, check each part:

```
$ aws cloudtrail describe-trails --query 'trailList[].[Name,IsMultiRegionTrail,LogFileValidationEnabled]' --output text
org-trail	True	True
$ aws cloudtrail get-trail-status --name org-trail --query IsLogging
true
$ aws configservice describe-configuration-recorder-status --query 'ConfigurationRecordersStatus[].[name,recording]' --output text
default	True
$ aws configservice describe-config-rules --query 'ConfigRules[].[ConfigRuleName,Source.SourceIdentifier]' --output text
ebs-encrypted	ENCRYPTED_VOLUMES
s3-versioning	S3_BUCKET_VERSIONING_ENABLED
```

(The emulator keeps these settings but records no events, evaluates no
rules, and does not support `lookup-events`; in a real account, event
history and rule results would fill in within minutes.)

## Check yourself

1. Someone terminated an instance last night. Which service says who?
   *CloudTrail.*
2. Was this security group open to the world last month? Which service?
   *AWS Config, from the group's configuration history.*
3. Does a default trail record S3 object reads?
   *No: those are data events, which must be added.*
4. Why multi-Region and log file validation?
   *Unused Regions are where an intruder would act; validation proves the
   logs were not altered.*
