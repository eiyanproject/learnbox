---
title: Infrastructure as code with CloudFormation
summary: The same resources described once in a template - parameters, intrinsic functions, outputs - and deployed as a stack you can update, review with change sets, protect and delete as one.
order: 3
files: [setup.sh, template.yaml]
run: awslab run setup.sh
hints:
  - "`!Ref Env` gives a parameter's value (or a resource's main ID); `!GetAtt DeadLetters.Arn` an attribute; `!Sub 'app-${Env}'` builds a string."
  - "The queue's redrive policy in YAML: `RedrivePolicy: {deadLetterTargetArn: !GetAtt DeadLetters.Arn, maxReceiveCount: 5}`."
  - "Bucket encryption in a template: `BucketEncryption: {ServerSideEncryptionConfiguration: [{ServerSideEncryptionByDefault: {SSEAlgorithm: aws:kms}}]}`; Block Public Access: `PublicAccessBlockConfiguration` with the four settings true."
  - "`aws cloudformation create-stack --stack-name app-dev --template-body file://template.yaml --parameters ParameterKey=Env,ParameterValue=dev --tags Key=env,Value=dev --enable-termination-protection`, then `aws cloudformation wait stack-create-complete --stack-name app-dev`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **infrastructure as code** | describing the end state, and letting a tool work out the calls |
| **end state** | what should exist, rather than the steps to make it |
| **CloudFormation** | AWS's infrastructure-as-code service |
| **template** | a YAML or JSON file declaring resources |
| **YAML** | a text format: indentation for nesting, `key: value` maps, `- item` lists |
| **stack** | the resources from one template, managed together |
| **resource** | one thing in the template, with a logical ID, `Type` and `Properties` |
| **logical ID** | the name you give a resource in the template, such as `Uploads` |
| **physical resource** | the real bucket or queue it creates, with its own name or ID |
| **`Type`** | the resource kind: `AWS::S3::Bucket`, `AWS::SQS::Queue` |
| **`Properties`** | its settings, named like the API's |
| **Parameters** | inputs given at deploy time; `AllowedValues` restricts them |
| **Outputs** | values the stack publishes |
| **Mappings**, **Conditions** | lookup tables (`!FindInMap`); create a resource only if true |
| **intrinsic function** | a function written with `!` in YAML |
| **`!Ref`** | a parameter's value, or a resource's main identifier |
| **`!GetAtt X.Attr`** | another attribute of a resource, such as its ARN |
| **`!Sub`** | a string with `${X}` values substituted |
| **dependency order** | references tell CloudFormation what to create first |
| **generated name** | a unique name made from the stack and logical ID when you give none |
| **`CREATE_IN_PROGRESS`** / **`CREATE_COMPLETE`** | being created / done |
| **roll back** | undo everything after a failure; ends in `ROLLBACK_COMPLETE` |
| **stack tags** | copied onto every resource in the stack |
| **update** | deploying a changed template; only differences change |
| **replacement** | a change that creates a new resource and deletes the old one, with its data |
| **change set** | a preview of an update, showing replacements |
| **termination protection** | refuses to delete the stack |
| **`DeletionPolicy`** | `Retain` or `Snapshot`: keep the resource when the stack is deleted; does not stop replacement |
| **drift detection** | finds changes made by hand behind the template's back |
| **AWS CDK** | writes CloudFormation templates from TypeScript or Python code |
| **Terraform**, **Pulumi** | independent infrastructure-as-code tools |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws cloudformation create-stack --stack-name N --template-body file://template.yaml --parameters ParameterKey=Env,ParameterValue=dev --tags Key=env,Value=dev --enable-termination-protection` | deploys a stack |
| `aws cloudformation wait stack-create-complete --stack-name N` | waits for it |
| `aws cloudformation describe-stacks --stack-name N` | shows status and outputs |
| `aws cloudformation describe-stack-resources --stack-name N` | maps logical IDs to real resources |
| `VersioningConfiguration`, `BucketEncryption`, `PublicAccessBlockConfiguration` | bucket properties used here |
| `MessageRetentionPeriod`, `VisibilityTimeout`, `RedrivePolicy` | queue properties |

### Errors

| Error | Means |
|---|---|
| `ValidationError` | a parameter outside `AllowedValues`, or deleting a protected stack (real CloudFormation) |

---

Everything in this course so far has been a script of CLI calls. That
works, but a script only knows how to **create** things. Run it a second
time and it fails, because everything already exists. Change one setting
in it, and it has no idea what to update, or what to delete when you remove
a line. And the account itself is the only record of what is really there.

**Infrastructure as code** turns this around: you describe the **end
state**, "a bucket with these settings, two queues wired like this", and a
tool works out which calls get there from whatever exists now.
**CloudFormation** is AWS's own such tool. You write a **template** (YAML or
JSON) that declares **resources**; deploying it creates a **stack**: those
resources, managed together as one unit.

```text
 template.yaml ──create-stack──> stack app-dev ──> bucket Uploads, queue DeadLetters, queue Jobs
       │ edit                        ▲
       └──change set (preview)───────┘   update: only what differs is changed
                                         delete: everything in the stack goes, unless protected
```

## A template

```yaml
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
Resources:
  Uploads:
    Type: AWS::S3::Bucket
    Properties:
      VersioningConfiguration: {Status: Enabled}
      Tags: [{Key: env, Value: !Ref Env}]
Outputs:
  UploadsBucket:
    Value: !Ref Uploads
```

A YAML reminder: indentation shows nesting (spaces, never tabs), `key:
value` pairs make a map, `- item` or `[a, b]` a list, and `{a: 1}` is a map
written on one line. Reading the template's sections:

- **Resources** (the only required section): each has a **logical ID** you
  choose (`Uploads`), a **Type** (`AWS::S3::Bucket`, `AWS::SQS::Queue`; the
  CloudFormation reference documents every type and its properties) and
  **Properties**. The property names match the API's settings: S3's
  versioning becomes `VersioningConfiguration`, SQS's `VisibilityTimeout`
  stays `VisibilityTimeout`.
- **Parameters** are inputs given at deploy time, so one template serves
  many environments. `AllowedValues` restricts them; real CloudFormation
  refuses any other value with a `ValidationError` before creating anything
  (the emulator does not check, so the lesson's check reads your template).
- **Outputs** publish values from the stack, such as a generated bucket
  name, for people and other stacks to read.

### Intrinsic functions

Resources refer to each other and to parameters through **intrinsic
functions**, written with a `!` in YAML's short form:

| Function | Gives | Example |
|---|---|---|
| `!Ref X` | a parameter's value, or a resource's main identifier (a bucket's name, a queue's URL) | `!Ref Env` is `dev` |
| `!GetAtt X.Attr` | another attribute of a resource | `!GetAtt DeadLetters.Arn` is the queue's ARN |
| `!Sub 'text ${X}'` | a string with values substituted | `!Sub 'app-${Env}-logs'` |

These references also tell CloudFormation the **order**: since `Jobs`
mentions `!GetAtt DeadLetters.Arn`, it creates `DeadLetters` first. You never
write the order yourself.

Leave out a bucket's name, as here, and CloudFormation generates a unique
one from the stack and logical ID (`app-dev-uploads-gnxtun0h40ga`). That is
what makes one template deployable many times; a fixed name could exist only
once in the world.

## Deploying

```
aws cloudformation create-stack --stack-name app-dev \
  --template-body file://template.yaml \
  --parameters ParameterKey=Env,ParameterValue=dev \
  --tags Key=env,Value=dev \
  --enable-termination-protection
aws cloudformation wait stack-create-complete --stack-name app-dev
```

`create-stack` returns at once with the stack's ID, while CloudFormation
creates the resources in the background; the stack's status moves from
`CREATE_IN_PROGRESS` to `CREATE_COMPLETE`. `wait stack-create-complete`
pauses until it is done. If any resource fails, CloudFormation **rolls
back**, deleting what it created, and the stack ends in `ROLLBACK_COMPLETE`:
all or nothing. Stack **tags** are copied onto every resource in the stack.

The outputs, afterwards:

```
$ aws cloudformation describe-stacks --stack-name app-dev --query 'Stacks[0].Outputs' --output table
-------------------------------------------------------------------------------------------------
|                                        DescribeStacks                                         |
+---------------+-------------------------------------------------------------------------------+
|   OutputKey   |                                  OutputValue                                  |
+---------------+-------------------------------------------------------------------------------+
|  UploadsBucket|  app-dev-uploads-gnxtun0h40ga                                                 |
|  JobsQueueUrl |  https://sqs.us-east-1.amazonaws.com/123456789012/app-dev-Jobs-99DHTELI3RF1   |
+---------------+-------------------------------------------------------------------------------+
```

## Changing a stack safely

Updating a stack means giving it a changed template; CloudFormation changes
only what differs. Some property changes can be made in place; others force
a **replacement**: a new resource is created, with a new ID, and the old one
deleted, **along with its data**. Renaming a database, for example, creates
a new, empty one. The tools for not being surprised:

- A **change set** previews an update before anything happens: which
  resources would be added, modified or removed, and for each modification
  whether it means **replacement**. You review it, then execute it (or
  throw it away). It shows intent; the update can still fail when run.
- **Termination protection** refuses to delete the whole stack until it is
  turned off. (Real CloudFormation refuses `delete-stack` with a
  `ValidationError`; the emulator does not enforce it.)
- A **DeletionPolicy** of `Retain` or `Snapshot` on a resource keeps it, or
  a snapshot of it, when the stack is deleted. ❗ It does not protect
  against **replacement** during an update: the old resource is still
  deleted.
- **Drift detection** compares the real resources with the template and
  reports what someone changed by hand behind its back. It only checks
  properties set in the template, and a manual change is undone at the
  stack's next update anyway, so change resources through the template.

Other tools work the same way with the same ideas: the **AWS CDK** writes
CloudFormation templates for you from TypeScript or Python code;
**Terraform** and **Pulumi** are independent tools that talk to the AWS API
directly.

## The other template sections

Besides Parameters, Resources and Outputs, a template can have:

- **Mappings**: lookup tables, such as an instance size per environment,
  read with `!FindInMap`;
- **Conditions**: create a resource only when a condition holds
  (`IsProd: !Equals [!Ref Env, prod]`, then `Condition: IsProd` on the
  resource);
- **Metadata** and a **Description**, for people and the console.

Each entry under Resources is a **logical** resource; the bucket or queue it
creates in the account is the **physical** resource, with its own name or
ID. A stack is the link between the two.

## Your task

Write **`template.yaml`** (the starter has empty sections) with:

- a parameter **`Env`** of type `String`, **`AllowedValues`** `dev` and
  `prod`;
- a bucket **`Uploads`**: versioning on (`VersioningConfiguration`),
  default encryption **SSE-KMS** (`SSEAlgorithm: aws:kms`), all four
  **Block Public Access** settings true (`PublicAccessBlockConfiguration`),
  and a tag **`env`** with the value **`!Ref Env`**;
- a queue **`DeadLetters`** keeping messages **14 days**
  (`MessageRetentionPeriod: 1209600`);
- a queue **`Jobs`** with a **120**-second `VisibilityTimeout`, and a
  `RedrivePolicy` to `DeadLetters` (`!GetAtt DeadLetters.Arn`) after **5**
  receives (in a template the redrive policy is a plain map, with no
  quoting puzzle);
- outputs **`UploadsBucket`** (`!Ref Uploads`) and **`JobsQueueUrl`**
  (`!Ref Jobs`).

Those three resources and nothing else. Then deploy it as the stack
**`app-dev`** with **Env=dev**, the stack tag **env=dev**, and **termination
protection** on, and wait for it to finish. After **Run**, `aws
cloudformation describe-stack-resources --stack-name app-dev --query
'StackResources[].[LogicalResourceId,ResourceType,PhysicalResourceId]'
--output table` maps each logical ID to the real resource CloudFormation
made.

## Check yourself

1. Run a CLI script twice and it fails; deploy a template twice and it does
   not. Why?
   *A template describes the end state; CloudFormation only changes what
   differs.*
2. What does `!GetAtt DeadLetters.Arn` give, and why does order not need
   writing down?
   *The queue's ARN; the reference tells CloudFormation to create
   DeadLetters first.*
3. A change set says "Replacement: True" for the database. What does that
   mean?
   *A new database is created and the old one deleted, with its data.*
4. Why leave the bucket name out of the template?
   *CloudFormation generates a unique one, so the template can be deployed
   many times.*
