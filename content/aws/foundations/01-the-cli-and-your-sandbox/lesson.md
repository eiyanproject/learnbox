---
title: The CLI and your sandbox account
summary: How an aws command is put together, who you are, which Region you are in, and your first two S3 buckets - one of them in Tokyo.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "Every command has the same shape: `aws <service> <operation> --option value`. `aws s3api create-bucket --bucket NAME` is service `s3api`, operation `create-bucket`."
  - "The default Region here is us-east-1. For the Tokyo bucket, add `--region ap-northeast-1` to the command."
  - "Outside us-east-1, S3 wants to be told where the bucket goes as well: `--create-bucket-configuration LocationConstraint=ap-northeast-1`. Leave it out and you get IllegalLocationConstraintException."
  - "Tags go on with `aws s3api put-bucket-tagging --bucket NAME --tagging 'TagSet=[{Key=project,Value=learnbox}]'`."
---

Everything in AWS is an API call. The console is a web page that makes the
calls for you; the **AWS CLI** makes them from a terminal, which means they
can be written down, repeated, reviewed and put in a script. That is how this
course works: every lesson's work is a script, `setup.sh`, and the check runs
it against an empty account and looks at what it built.

## Your sandbox account

The `aws` command in the terminal is the real AWS CLI. It is pointed at
**moto**, an emulator of the AWS APIs running inside this box, so:

- there is no AWS account, no password and no bill;
- nothing you type reaches the real AWS;
- the account lives in memory - `awslab reset` empties it.

Try it. In the terminal:

```
aws sts get-caller-identity
```

STS (Security Token Service) answers "who am I?". The reply names an
**account** (a 12-digit number - here the emulator's `123456789012`) and an
**ARN**, the Amazon Resource Name that identifies anything in AWS:

```
arn:aws:sts::123456789012:user/moto
arn:partition:service:region:account-id:resource
```

The Region part is empty because identities are global, not Regional. (A
real account answers with an `arn:aws:iam::...` ARN for an IAM user; the
emulator says `sts`. Same shape.)

## The shape of a command

```
aws  <service>  <operation>  --option value ...
aws  s3api      list-buckets
aws  ec2        describe-regions  --output table
```

`aws help`, `aws s3api help` and `aws s3api create-bucket help` show the
manual at each level. Three options work on every command:

| Option | What it does |
|---|---|
| `--region ap-northeast-1` | Which Region to call. Most services are Regional. |
| `--output json\|table\|text` | How to print the answer. JSON is the default. |
| `--query 'Buckets[].Name'` | Pick fields out of the answer (JMESPath). |

`--query` is worth learning early. `aws s3api list-buckets --query
'Buckets[].Name' --output text` prints just the names, ready for a script.

## Regions and Availability Zones

A **Region** (`us-east-1`, `ap-northeast-1` for Tokyo) is a separate
geographic area with its own copy of most services. Inside each are several
**Availability Zones** - separate data centres with their own power and
networking, close enough for fast links. Resilient designs spread across AZs;
some go further and use more than one Region.

`aws ec2 describe-availability-zones --region ap-northeast-1 --query
'AvailabilityZones[].ZoneName'` lists Tokyo's.

## S3 buckets

S3 stores objects in **buckets**. A bucket name is global - unique across
every AWS account in the world - and the bucket itself lives in one Region.
There are two CLIs for S3: `aws s3` (high level: `mb`, `cp`, `sync`, `ls`)
and `aws s3api` (one command per API call). This lesson uses `s3api`, because
it shows what is really being asked:

```
aws s3api create-bucket --bucket my-example-bucket
```

Outside us-east-1 the call also has to say where the bucket goes:

```
aws s3api create-bucket --bucket my-example-bucket \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1
```

## Your task

Fill in `setup.sh` so that it:

1. creates a bucket named **`lb-first-bucket`** in us-east-1;
2. tags it **`project=learnbox`**;
3. creates a bucket named **`lb-tokyo-bucket`** in **ap-northeast-1**.

Press **Run** to try it against your sandbox: it empties the account, runs the
script and shows every command. Then look around - `aws s3api list-buckets`,
`aws s3api get-bucket-location --bucket lb-tokyo-bucket`. **Check** runs it
again against a fresh account and inspects the result.
