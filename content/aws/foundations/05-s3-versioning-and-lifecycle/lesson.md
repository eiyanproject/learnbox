---
title: S3 objects, versioning and lifecycle
summary: Putting and getting objects, keeping every version of them, and letting lifecycle rules move old data to cheaper storage classes and delete it when it is done.
order: 5
files: [setup.sh, lifecycle.json]
run: awslab run setup.sh
hints:
  - "`aws s3api put-bucket-versioning --bucket lb-logs --versioning-configuration Status=Enabled` - before the uploads, or the first one has no version to keep."
  - "Upload the same key twice: `aws s3 cp app.log s3://lb-logs/logs/app.log` (the script makes app.log; change it between uploads with `echo more >> app.log`)."
  - "A lifecycle rule needs an ID, `\"Status\": \"Enabled\"` and a Filter: `\"Filter\": {\"Prefix\": \"logs/\"}`. Transitions are a list: `[{\"Days\": 30, \"StorageClass\": \"STANDARD_IA\"}, {\"Days\": 90, \"StorageClass\": \"GLACIER\"}]`."
  - "`\"Expiration\": {\"Days\": 365}` ends current versions; `\"NoncurrentVersionExpiration\": {\"NoncurrentDays\": 30}` ends the old ones. `aws s3api put-bucket-lifecycle-configuration --bucket lb-logs --lifecycle-configuration file://lifecycle.json`."
---

S3 stores **objects** - any bytes, up to 5 TB each - under **keys** in a
bucket. There are no real folders: `logs/2026/app.log` is one key, and the
console draws folders from the slashes.

```
aws s3 cp app.log s3://lb-logs/logs/app.log        # upload
aws s3 ls s3://lb-logs/logs/                        # list
aws s3 cp s3://lb-logs/logs/app.log -              # download to stdout
aws s3api head-object --bucket lb-logs --key logs/app.log   # metadata only
```

S3 is designed for **eleven nines** of durability (99.999999999%): objects
are stored redundantly across at least three Availability Zones (except the
One Zone classes).

## Versioning

With **versioning** on, overwriting or deleting an object keeps the old one.
Every upload gets a **version ID**; a delete just adds a *delete marker* on
top, and removing the marker brings the object back. It is the cheapest
protection there is against an accidental overwrite or a ransomware run -
and a prerequisite for replication and Object Lock.

Versioning can be **enabled** or **suspended**, never switched off again.
Old versions are billed like any object, which is where lifecycle comes in.

## Storage classes

| Class | For | Notes |
|---|---|---|
| S3 Standard | data used often | the default |
| S3 Intelligent-Tiering | unknown or changing access | moves objects between tiers itself; small monitoring fee |
| S3 Standard-IA | used rarely, needed fast | cheaper storage, a fee per GB retrieved; 30-day minimum |
| S3 One Zone-IA | re-creatable data | one AZ only - not for the only copy |
| S3 Glacier Instant Retrieval | archive read a few times a year | milliseconds to read |
| S3 Glacier Flexible Retrieval | archive | minutes to hours to restore (API name `GLACIER`) |
| S3 Glacier Deep Archive | long-term retention | cheapest; hours to restore |

## Lifecycle rules

A **lifecycle configuration** tells S3 to act on objects by age:
**transitions** move them to a cheaper class, **expiration** deletes them.
Rules can apply to a prefix or a tag, and to current or *noncurrent* (old)
versions separately.

```json
{
  "Rules": [{
    "ID": "archive-logs",
    "Status": "Enabled",
    "Filter": { "Prefix": "logs/" },
    "Transitions": [
      { "Days": 30, "StorageClass": "STANDARD_IA" }
    ],
    "Expiration": { "Days": 365 }
  }]
}
```

## Your task

1. Turn on **versioning** for the bucket `lb-logs` (the script creates it).
2. Upload `app.log` to **`logs/app.log`**, change it, and upload it again, so
   the key has **two versions**.
3. Write **`lifecycle.json`** with one rule for the prefix **`logs/`** that
   moves objects to **STANDARD_IA after 30 days**, to **GLACIER after 90**,
   expires them after **365**, and deletes **noncurrent versions 30 days**
   after they are replaced. Apply it.

Then `aws s3api list-object-versions --bucket lb-logs --prefix logs/` shows
both versions, newest marked `IsLatest`.
