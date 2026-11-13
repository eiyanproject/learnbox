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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **object** | any bytes stored in S3, up to 5 TB |
| **key** | an object's full name, such as `logs/2026/app.log`; there are no real folders |
| **prefix** | the start of a key, such as `logs/`; many features select objects by it |
| **metadata** | facts about an object (size, type, date) rather than its content |
| **durability** | how unlikely data loss is; S3 is designed for eleven nines (99.999999999%) |
| **versioning** | keep every old copy when an object is overwritten or deleted |
| **version** / **version ID** | one stored copy of a key / its identifier |
| **current** / **noncurrent version** | the newest version / any older one |
| **`null` version ID** | an object stored before versioning was turned on |
| **delete marker** | a newest "version" that hides the object; removing it brings the object back |
| **enabled** / **suspended** | versioning's two states once turned on; it can never be switched off |
| **replication** | copying objects to another bucket automatically; needs versioning |
| **Object Lock** | stops objects being deleted or changed for a set time; needs versioning |
| **ransomware** | malware that overwrites files with encrypted copies |
| **storage class** | a trade-off between storage price and read price and speed |
| **S3 Standard** | the default class, for data used often |
| **Intelligent-Tiering** | moves objects between tiers itself |
| **Standard-IA** | Infrequent Access: cheaper storage, a fee per GB read |
| **One Zone-IA** | stored in one AZ only; for data you can re-create |
| **Glacier Instant / Flexible Retrieval / Deep Archive** | archive classes: milliseconds / minutes to hours / up to 12 hours to read back |
| **restore** | make a Glacier Flexible or Deep Archive object readable again: Expedited, Standard or Bulk |
| **minimum storage duration** | days billed even if deleted sooner: 30 (IA), 90 (Glacier Instant, Flexible), 180 (Deep Archive) |
| **minimum billable size** | IA classes and Glacier Instant bill each object as at least 128 KB |
| **lifecycle configuration** | rules S3 applies to objects by age, once a day |
| **transition** | move objects to a colder class after some days; never back up |
| **expiration** | delete objects after some days (in a versioned bucket: add a delete marker) |
| **noncurrent version expiration** | delete old versions some days after they were replaced |
| **`Filter`** | which objects a rule applies to, by prefix or tag |
| **XML** | the text format S3's API uses underneath; the CLI converts your JSON |
| **MFA Delete** | requires an MFA code to delete a version or suspend versioning; root only |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws s3 cp FILE s3://bucket/key` | uploads a file |
| `aws s3 cp s3://bucket/key -` | downloads it to the terminal |
| `aws s3 ls s3://bucket/prefix/` | lists objects |
| `aws s3 rm s3://bucket/key` | deletes (in a versioned bucket: adds a delete marker) |
| `aws s3api head-object --bucket B --key K` | shows an object's metadata |
| `aws s3api put-bucket-versioning --bucket B --versioning-configuration Status=Enabled` | turns versioning on |
| `aws s3api list-object-versions --bucket B --prefix P` | lists every version |
| `aws s3api delete-object --bucket B --key K --version-id V` | really deletes one version |
| `aws s3api put-bucket-lifecycle-configuration --bucket B --lifecycle-configuration file://lifecycle.json` | sets (replaces) the lifecycle rules |
| `aws s3api get-bucket-lifecycle-configuration --bucket B` | shows the rules |
| `STANDARD_IA`, `GLACIER` | API names of the Standard-IA and Glacier Flexible Retrieval classes |
| `Transitions`, `Expiration`, `NoncurrentVersionExpiration` | the rule's actions in `lifecycle.json` |

### Errors

| Error | Means |
|---|---|
| `MalformedXML ... did not validate against our published schema` | a lifecycle rule without a `Filter`, or another shape mistake |

---

Two things go wrong with stored data over time: someone overwrites or
deletes a file they needed, and old data piles up, costing money for files
nobody reads. This lesson handles both for a bucket of application logs:
**versioning** keeps every old copy, and a **lifecycle rule** moves old logs
to cheaper storage and eventually deletes them, without anyone having to
remember to.

## Objects and keys

S3 stores **objects** (any bytes, up to 5 TB each) under **keys** in a
bucket. A key is simply the object's full name. There are no real folders:
`logs/2026/app.log` is one key, and the console draws folders from the
slashes. A part of a key such as `logs/` is called a **prefix**, and many S3
features, lifecycle rules among them, select objects by prefix.

The high-level `aws s3` commands move files:

```
aws s3 cp app.log s3://lb-logs/logs/app.log                  # upload
aws s3 ls s3://lb-logs/logs/                                  # list
aws s3 cp s3://lb-logs/logs/app.log -                        # download, printed to the terminal
aws s3api head-object --bucket lb-logs --key logs/app.log     # metadata only, no content
```

An upload reports what it did:

```
upload: ./app.log to s3://lb-logs/logs/app.log
```

S3 is designed for **eleven nines** of durability (99.999999999%): each
object is stored redundantly across at least three Availability Zones
(except in the One Zone classes below). Losing an object to hardware
failure is practically impossible. Losing it to a mistaken overwrite or
delete is easy, which is what versioning is for.

## Versioning

With **versioning** on, uploading to a key that already exists does not
replace the old object: it adds a new **version** on top, and the old one is
kept. Every version gets a **version ID**, and a plain `get` returns the
newest, the **current** version. The others are **noncurrent**.

```
$ aws s3api list-object-versions --bucket lb-logs --prefix logs/ \
    --query 'Versions[].[VersionId,IsLatest,Size]' --output table
---------------------------------------------------------
|                  ListObjectVersions                   |
+---------------------------------------+--------+------+
|  641e1f14-d3f6-48bc-aaf4-b91f10bb7400 |  True  |  23  |
|  0d22281a-0347-451d-96f6-31de80654e80 |  False |  11  |
+---------------------------------------+--------+------+
```

Two uploads of `logs/app.log`: the 23-byte one is current (`IsLatest`), the
first, 11-byte one is still there. Deleting is gentler too: `aws s3 rm`
on a versioned key does not destroy anything, it adds a **delete marker** as
the newest version, so the object seems gone (`aws s3 ls` no longer shows
it), while every version stays underneath. Removing the delete marker
brings the object back. Only deleting a specific version ID
(`delete-object --version-id ...`) really removes data.

That makes versioning the cheapest protection there is against an accidental
overwrite, or ransomware that overwrites files with encrypted copies. It is
also required by replication to another bucket and by Object Lock.

Three things to know:

- Versioning can be **enabled** or **suspended**, never switched off again.
  Suspending stops new versions; old ones stay.
- Turn it on **before** the uploads you want protected: an object uploaded
  while versioning was off has no earlier version to fall back to. Objects
  that existed before versioning was enabled show the version ID `null`.
- 💸 Every noncurrent version is billed like any other object, in full:
  S3 stores whole copies, not the differences. A log
  rewritten every hour keeps 8,760 copies a year. That is where lifecycle
  rules come in.

## Storage classes

Each object has a **storage class**, a trade-off between the price of
storing it and the price and speed of reading it back:

| Class | For | Notes |
|---|---|---|
| S3 Standard | data used often | the default |
| S3 Intelligent-Tiering | unknown or changing access patterns | moves objects between tiers itself; small monitoring fee per object |
| S3 Standard-IA (Infrequent Access) | used rarely, needed fast | cheaper storage, a fee per GB read; billed for at least 30 days |
| S3 One Zone-IA | data you can re-create | stored in one AZ only: never for the only copy |
| S3 Glacier Instant Retrieval | archive read a few times a year | milliseconds to read |
| S3 Glacier Flexible Retrieval | archive | minutes to hours to restore before reading (API name `GLACIER`) |
| S3 Glacier Deep Archive | long-term retention, years | cheapest storage; up to 12 hours to restore |

Each class except Standard and Intelligent-Tiering also has a **minimum
storage duration**, billed even if the object is deleted sooner: 30 days for
Standard-IA and One Zone-IA, 90 days for Glacier Instant and Flexible
Retrieval, 180 days for Deep Archive. Standard-IA, One Zone-IA and Glacier
Instant Retrieval also bill every object as at least 128 KB, so millions of
tiny files cost more there than in Standard.

Exam questions turn on the words in the right-hand column: "accessed
rarely but must be available immediately" is Standard-IA or Glacier Instant
Retrieval; "can wait hours" is Glacier Flexible Retrieval or Deep Archive;
"can be re-created" allows One Zone. The minimum-duration charges matter
too: moving an object to Standard-IA and deleting it a week later still
bills 30 days.

## Lifecycle rules

A **lifecycle configuration** is a set of rules that S3 applies to objects
by age, once a day, by itself, to existing objects as well as new ones:

- **transitions** move objects to a cheaper storage class after a number of
  days;
- **expiration** deletes them. In a versioned bucket it only adds a delete
  marker to the current version, so the data stays (and is billed) until a
  noncurrent version expiration removes the old versions too;
- **noncurrent version** actions do the same for old versions, counted from
  when each was replaced.

Each rule selects its objects with a **Filter**, by prefix or by tag:

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

Read it as "for objects under `logs/`: after 30 days, move to Standard-IA;
after 365 days, expire". A rule without a `Filter` is refused with
`MalformedXML ... did not validate against our published schema` (S3's
API is XML underneath; the CLI converts your JSON). `put-bucket-lifecycle-configuration`
**replaces** the bucket's whole configuration, so all rules go in one
document.

## Two more S3 details

- **MFA Delete**, an option of versioning, requires an MFA code to delete a
  version or to suspend versioning: protection against a stolen password.
  Only the root user can turn it on.
- Restoring from **Glacier Flexible Retrieval** comes in three speeds:
  Expedited (1-5 minutes), Standard (3-5 hours) and Bulk (5-12 hours), the
  faster the dearer. Until restored, an object there cannot be read at all.
- Lifecycle transitions only go **down** to colder classes, never back up,
  and an object must have been stored 30 days before it can move to
  Standard-IA or One Zone-IA.

## Your task

1. Turn on **versioning** for the bucket `lb-logs` (the script creates it),
   before any upload.
2. Upload `app.log` (the script makes it) to **`logs/app.log`**, change the
   file, and upload it again, so the key has **two versions**, the newer one
   containing the change.
3. Write **`lifecycle.json`** with **one** rule for the prefix **`logs/`**
   (two rules for the same prefix can contradict each other, and the check
   refuses that) which:
   - is enabled;
   - moves objects to **STANDARD_IA after 30 days**, and to **GLACIER after
     90**;
   - expires them after **365** days;
   - deletes **noncurrent versions 30 days** after they are replaced.

   Apply it to the bucket.

After **Run**, `aws s3api list-object-versions --bucket lb-logs --prefix
logs/` shows both versions, the newest marked `IsLatest`, and
`aws s3api get-bucket-lifecycle-configuration --bucket lb-logs` shows the
rule as S3 stored it. (The emulator stores the rule but does not move or
delete anything over time; real S3 does.)

## Check yourself

1. Versioning is on, and someone runs `aws s3 rm` on a key. Is the data
   gone?
   *No: a delete marker hides it; the versions are still there and still
   billed.*
2. Can versioning be turned off again?
   *No, only suspended. Old versions stay.*
3. Reports are read once a quarter but must open instantly. Which class?
   *Standard-IA, or Glacier Instant Retrieval for even cheaper storage.*
4. Why would moving millions of 10 KB files to Standard-IA cost more?
   *Each object is billed as at least 128 KB.*
5. A versioned bucket's lifecycle rule has `Expiration` only. Do old
   versions ever leave?
   *No: that needs `NoncurrentVersionExpiration` too.*
