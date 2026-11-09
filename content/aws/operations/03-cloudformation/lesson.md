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

Everything in this course so far has been a script of CLI calls. It works,
but a script only knows how to *create* things: run it twice and it fails,
change it and it does not know what to update or delete. **Infrastructure as
code** describes the **end state** instead, and lets a tool work out the
calls.

**CloudFormation** is AWS's own. A **template** (YAML or JSON) declares
**resources**; deploying it creates a **stack** - the resources, managed as
one unit. Update the template and CloudFormation changes only what differs;
delete the stack and everything in it goes (unless protected).

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

- **Parameters** make one template serve many environments.
- **Intrinsic functions**: `!Ref`, `!GetAtt`, `!Sub`, `!Join`, `!If`... wire
  resources together, so CloudFormation knows the order to create them in.
- **Outputs** publish values (and can be exported for other stacks).
- Leaving out a bucket name lets CloudFormation generate a unique one - which
  is what makes one template deployable many times.

## Changing a stack safely

- A **change set** previews an update: which resources change, and whether
  any will be **replaced** (a new resource, new ID, data gone with the old
  one).
- **Termination protection** stops the stack from being deleted.
- A **DeletionPolicy: Retain** or **Snapshot** keeps a resource's data when
  the stack goes.
- **Drift detection** finds what someone changed by hand behind the
  template's back.

Other tools do the same job - the **AWS CDK** (CloudFormation written in
TypeScript, Python...), **Terraform**, **Pulumi** - with the same ideas.

## Your task

Write **`template.yaml`** with:

- a parameter **`Env`**, allowed values **dev** and **prod**;
- a bucket **`Uploads`**: versioning on, **SSE-KMS** default encryption, all
  four **Block Public Access** settings, tagged **`env`** = the parameter;
- a queue **`DeadLetters`** keeping messages **14 days**;
- a queue **`Jobs`** with a **120** s visibility timeout, redriving to
  `DeadLetters` after **5** receives (`!GetAtt DeadLetters.Arn`);
- outputs **`UploadsBucket`** and **`JobsQueueUrl`**.

Then deploy it as the stack **`app-dev`** with **Env=dev**, the stack tag
**env=dev**, and **termination protection** on.
