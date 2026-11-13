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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **AWS** | Amazon Web Services: servers, storage, databases and networks rented by the hour or by the request |
| **API call** | a request to one of AWS's web services, such as "create a bucket" |
| **console** | the AWS website; it makes API calls for you when you click |
| **AWS CLI** | the `aws` command: makes the same API calls from a terminal |
| **SDK** | a library that lets a program (Python, Java, JavaScript...) make the calls |
| **moto** | an emulator of the AWS APIs running inside this box; nothing reaches real AWS |
| **sandbox account** | the emulated, in-memory account each Run starts from empty |
| **STS** | Security Token Service; answers "who am I?" |
| **account** | a 12-digit number that owns resources and gets the bill |
| **ARN** | Amazon Resource Name: `arn:partition:service:region:account-id:resource` |
| **partition** | the first part of an ARN: `aws` for normal Regions, `aws-cn` for China |
| **global** | not tied to one Region, such as identities (the ARN's Region part is empty) |
| **service** | the part of AWS to call: `s3api`, `ec2`, `iam` |
| **operation** | the API call itself: `create-bucket`, `describe-regions` |
| **option** | a parameter of the call, written `--name value` |
| **JMESPath** | the query language `--query` uses to pick fields out of a JSON answer |
| **JSON** | the text format AWS answers in: `{ "key": "value" }` and `[ lists ]` |
| **Region** | a separate geographic area, such as `us-east-1` or `ap-northeast-1` (Tokyo), with its own copy of most services |
| **Regional** | existing in one Region only; invisible from the others |
| **Availability Zone (AZ)** | a separate data centre (or group) inside a Region, with its own power and network |
| **AZ ID** | a zone's fixed name, such as `apne1-az4`, the same in every account; the letters in AZ names are shuffled per account |
| **S3** | Simple Storage Service: stores files in buckets |
| **object** | a file stored in S3 |
| **bucket** | a container of objects; its name is unique worldwide, and it lives in one Region |
| **endpoint** | the web address a call is sent to; `--region` picks it |
| **location constraint** | the Region a new bucket goes in, given in the request body; us-east-1 reports `null` |
| **tag** | a key-value label on a resource, such as `project=learnbox` |
| **TagSet** | the whole list of a bucket's tags, set all at once |
| **shorthand** | the CLI's compact way of writing JSON: `'TagSet=[{Key=k,Value=v}]'` |
| **error code** | the name in brackets in an error, such as `IllegalLocationConstraintException`; what to search for |
| **exit status** | the number a command ends with: 0 for success; the CLI uses 255 for an error |
| **shell script** | a file of commands run one after another; here `setup.sh` |
| **credentials** | the keys that prove who is calling; the sandbox supplies fake ones |
| **single sign-on (SSO)** | one sign-in that gives access to several accounts |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws <service> <operation> --option value` | the shape of every AWS CLI command |
| `aws sts get-caller-identity` | shows the account, user ID and ARN you are calling as |
| `aws s3api list-buckets` | lists your buckets |
| `aws ec2 describe-regions` | lists the Regions |
| `aws ec2 describe-availability-zones --region R` | lists a Region's AZs |
| `aws s3api create-bucket --bucket NAME` | creates a bucket in the default Region |
| `--create-bucket-configuration LocationConstraint=R` | says which Region the bucket goes in, needed outside us-east-1 |
| `aws s3api put-bucket-tagging --bucket NAME --tagging 'TagSet=[...]'` | sets the bucket's tags; prints nothing on success |
| `aws s3api get-bucket-tagging --bucket NAME` | shows the bucket's tags |
| `aws s3api get-bucket-location --bucket NAME` | shows the bucket's Region |
| `aws s3 mb`, `cp`, `sync`, `ls` | the high-level S3 commands for moving files |
| `--region R` | which Region to call |
| `--output json\|table\|text` | how to print the answer |
| `--query 'Buckets[].Name'` | picks fields out of the answer |
| `ID=$(aws ... --query X --output text)` | saves one value in a shell variable |
| `aws help`, `aws s3api help`, `aws s3api create-bucket help` | the manual at each level |
| `aws configure`, `aws configure sso` | sets up credentials on a real CLI |
| `awslab reset` | empties the sandbox account |
| `\` at the end of a line | continues the command on the next line |
| `#!/usr/bin/env bash` | first line of a script: run it with bash |
| `set -euo pipefail` | stop at the first failure (`-e`), on unset variables (`-u`), and on a failure inside a pipeline |

### Errors

| Error | Means |
|---|---|
| `An error occurred (CODE) when calling the OPERATION operation: message` | the shape of every CLI error |
| `IllegalLocationConstraintException` | a bucket outside us-east-1 created without `--create-bucket-configuration` |
| `setup.sh exited 255` | a command in the script failed and `set -e` stopped it |

---

**AWS** (Amazon Web Services) rents out computing as a service: servers,
storage, databases, networks, by the hour or by the request. Everything in
it is an **API call**: a request to one of its web services, such as "create
a bucket" or "start a server". The web console is a website that makes those
calls for you when you click. The **AWS CLI** (command line interface) makes
them from a terminal, which means they can be written down, repeated,
reviewed and put in a script.

That is how this course works: every lesson's work is a shell script,
`setup.sh`, and the check runs it against an empty account and looks at what
it built. This first lesson covers the shape of every command, who you are
and where you are working, and ends with two storage buckets.

## Your sandbox account

The `aws` command in this terminal is the real AWS CLI, version 1. It is
pointed at **moto**, an emulator of the AWS APIs running inside this box:
a program that answers the same requests the way AWS would. So:

- there is no AWS account, no password and no bill;
- nothing you type reaches the real AWS;
- the account lives in memory: `awslab reset` empties it.

Try it. In the terminal (the `$` is the prompt, not part of the command):

```
$ aws sts get-caller-identity
{
    "UserId": "AKIAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:user/moto"
}
```

STS, the **Security Token Service**, answers "who am I?". The reply names
an **account**, a 12-digit number (here the emulator's `123456789012`;
every real account has its own), and an **ARN**.

An **ARN** (Amazon Resource Name) identifies anything in AWS, and every ARN
has the same parts, separated by colons:

```
arn:aws:sts::123456789012:user/moto
arn:partition:service:region:account-id:resource
```

The **partition** is `aws` for the normal regions (`aws-cn` for China). The
Region part is empty here because identities are global, not tied to one
Region. (A real account answers with an `arn:aws:iam::...` ARN for an IAM
user; the emulator says `sts`. Same shape.) You will read and write ARNs in
almost every lesson.

## The shape of a command

Every command has the same three parts:

```
aws  <service>  <operation>  --option value ...
aws  s3api      list-buckets
aws  ec2        describe-regions  --output table
```

The **service** is the AWS service to call (`s3api`, `ec2`, `iam`), the
**operation** is the API call (`create-bucket`, `describe-regions`), and the
options are its parameters. `aws help`, `aws s3api help` and
`aws s3api create-bucket help` show the manual at each level, with every
option the call accepts.

Three options work on every command:

| Option | What it does |
|---|---|
| `--region ap-northeast-1` | Which Region to call. Most services are Regional. |
| `--output json\|table\|text` | How to print the answer. JSON is the default. |
| `--query 'Buckets[].Name'` | Pick fields out of the answer, using the JMESPath query language. |

`--query` is worth learning early, because scripts need single values rather
than whole JSON documents. `Buckets[].Name` means "the `Name` of every item
in the `Buckets` list":

```
$ aws s3api list-buckets --query 'Buckets[].Name' --output text
lb-first-bucket	lb-tokyo-bucket
```

With `--output text` the names come out separated by tabs, ready for a
script, instead of as a JSON list. Later lessons capture a single value this
way into a shell variable, as in `ID=$(aws ... --query X --output text)`.

## Regions and Availability Zones

A **Region** is a separate geographic area, such as `us-east-1` (northern
Virginia) or `ap-northeast-1` (Tokyo), with its own independent copy of most
services. Resources you create in one Region are not visible from another:
asking us-east-1 for a Tokyo server finds nothing. Commands go to the
default Region, us-east-1 in this sandbox, unless you pass `--region`.

Inside each Region are several **Availability Zones** (AZs): separate data
centres, or groups of them, with their own power, cooling and networking,
far enough apart that a fire or flood takes out one, and close enough for
fast links between them. Designs that must survive a failure spread across
AZs; some go further and use more than one Region.

```
$ aws ec2 describe-availability-zones --region ap-northeast-1 --query 'AvailabilityZones[].ZoneName'
[
    "ap-northeast-1a",
    "ap-northeast-1c",
    "ap-northeast-1d"
]
```

AZ names are the Region plus a letter. (There is no `1b`: Tokyo does not
offer it to new accounts.) The letters are shuffled per account, so your
`ap-northeast-1a` may be a different data centre from someone else's; the
**AZ ID** (`apne1-az4`) is the same for everyone, and is what to compare
across accounts.

## S3 buckets

**S3** (Simple Storage Service) stores files, called **objects**, in
containers called **buckets**. Two rules about buckets surprise people:

- A bucket's **name is global**: unique across every AWS account in the
  world, because it becomes part of a web address. `lb-first-bucket` may
  already be taken in real AWS; in this sandbox it is yours. Names are 3 to
  63 characters of lower-case letters, digits, dots and hyphens.
- The bucket itself **lives in one Region**, and its data stays there.

There are two CLIs for S3: `aws s3` (high level: `mb`, `cp`, `sync`, `ls`,
for moving files around) and `aws s3api` (one command per API call). This
lesson uses `s3api`, because it shows what is really being asked:

```
$ aws s3api create-bucket --bucket my-example-bucket
{
    "Location": "/my-example-bucket"
}
```

Outside us-east-1 the call also has to say where the bucket goes, both with
`--region` (which endpoint to call) and in the request body:

```
aws s3api create-bucket --bucket my-example-bucket \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1
```

The `\` at the end of a line continues the command on the next line, so a
long command can be read one option per line. Leave out
`--create-bucket-configuration` and S3 refuses:

```
An error occurred (IllegalLocationConstraintException) when calling the CreateBucket operation: The unspecified location constraint is incompatible for the region specific endpoint this request was sent to.
```

Every CLI error has this shape: an error **code** in brackets
(`IllegalLocationConstraintException`), the **operation** that failed
(`CreateBucket`), then a message. The code is what to search for.

### Tags

A **tag** is a key-value label you attach to a resource, such as
`project=learnbox`. AWS does nothing with tags by itself; people use them to
find resources, split the bill by project, and limit permissions. S3 sets a
bucket's tags all at once, as a `TagSet` list:

```
aws s3api put-bucket-tagging --bucket lb-first-bucket \
  --tagging 'TagSet=[{Key=project,Value=learnbox}]'
```

The `'TagSet=[{Key=...,Value=...}]'` form is the CLI's **shorthand** for a
JSON structure; the single quotes stop the shell from interpreting the
brackets. `put-bucket-tagging` prints nothing when it succeeds, as many
"put" and "update" calls do.

## The script, and how Run shows it

The starter `setup.sh` begins with two lines you will see in every lesson:

```
#!/usr/bin/env bash
set -euo pipefail
```

The first says "run this with bash". The second makes the script **stop at
the first failing command** instead of carrying on with half the work done:
`-e` stops on an error, `-u` treats a misspelt, unset variable as an error,
and `-o pipefail` catches a failure in the middle of a `|` pipeline.

**Run** empties the sandbox account and runs your script, showing each
command and its answer. When a command fails, the output ends with the error
and the exit status:

```
awslab: empty sandbox account, region us-east-1; running setup.sh

$ aws s3api create-bucket --bucket lb-first-bucket
{
    "Location": "/lb-first-bucket"
}
$ aws s3api create-bucket --bucket lb-tokyo-bucket --region ap-northeast-1

An error occurred (IllegalLocationConstraintException) when calling the CreateBucket operation: ...

awslab: setup.sh exited 255. What it built is still there - look around with aws, or `awslab reset` to clear it.
```

## Three ways in, one API

The console, the CLI and the **SDKs** (libraries for Python, JavaScript,
Java and other languages that programs use) are three front ends to the
same API calls. Whatever one can do, the others can too, and the
permissions that apply are the same. A real CLI is configured with
credentials first (`aws configure`, or `aws configure sso` for single
sign-on); in this sandbox the wrapper does that for you, with fake keys the
emulator accepts.

## Your task

Fill in `setup.sh` so that it:

1. creates a bucket named **`lb-first-bucket`** in us-east-1, the default
   Region;
2. tags it **`project=learnbox`**;
3. creates a bucket named **`lb-tokyo-bucket`** in **ap-northeast-1**.

Press **Run** to try it, then look around:

```
$ aws s3api get-bucket-location --bucket lb-tokyo-bucket
{
    "LocationConstraint": "ap-northeast-1"
}
$ aws s3api get-bucket-location --bucket lb-first-bucket
{
    "LocationConstraint": null
}
```

The `null` is not a mistake: S3 reports us-east-1 as "no location
constraint", a quirk from before it had other Regions. The check accepts
that. `aws s3api get-bucket-tagging --bucket lb-first-bucket` shows the tag.
**Check** runs your script again against a fresh account and inspects the
result.

## Check yourself

1. What are the parts of `aws ec2 describe-regions --output table`?
   *Service `ec2`, operation `describe-regions`, and an option choosing the
   output format.*
2. A bucket called `lb-tokyo-bucket` is in ap-northeast-1. Why can't someone
   else create `lb-tokyo-bucket` in eu-west-1?
   *Bucket names are global, unique across every account and Region.*
3. `get-bucket-location` returns `null`. Where is the bucket?
   *In us-east-1: S3 reports it as having no location constraint.*
4. Why does the Run output end with `exited 255` when a command fails?
   *`set -e` stops the script at the first failing command, and the CLI
   exits with status 255 on an error.*
