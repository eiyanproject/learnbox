---
title: CodeBuild and CodePipeline
summary: A buildspec that runs the tests and reports them, a CodeBuild project with a least-privilege role and a secret, and a four-stage pipeline - source, build, manual approval, CloudFormation deploy - over an encrypted, versioned artifact bucket, started by an EventBridge rule.
order: 1
files: [setup.sh, buildspec.yml]
run: awslab run setup.sh
hints:
  - "buildspec.yml: `version: 0.2`, `env: {secrets-manager: {SONAR_TOKEN: ci/sonar-token}}`, `phases: {install: {runtime-versions: {python: \"3.12\"}}, build: {commands: [...]}}`, `reports: {unit-tests: {files: [junit.xml], base-directory: reports, file-format: JUNITXML}}`, `artifacts: {files: [template.yaml]}`."
  - "`aws codebuild create-project --name orders-api-build --source type=S3,location=lb-pipeline-artifacts/source/orders-api.zip --artifacts type=NO_ARTIFACTS --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL --service-role \"$BUILD_ROLE\" --timeout-in-minutes 20`."
  - "Write the pipeline as JSON with python3 and `aws codepipeline create-pipeline --cli-input-json file://pipeline.json`. Each action has `name`, `actionTypeId` (`category`, `owner: AWS`, `provider`, `version: \"1\"`), `configuration`, and `inputArtifacts` / `outputArtifacts` by name."
  - "The deploy action's configuration: `ActionMode: CREATE_UPDATE`, `StackName: orders-api`, `TemplatePath: BuildOutput::template.yaml`, `RoleArn: <cfn-deploy ARN>`."
  - "Turn on S3 events to EventBridge with `aws s3api put-bucket-notification-configuration --bucket lb-pipeline-artifacts --notification-configuration '{\"EventBridgeConfiguration\": {}}'`, then `aws events put-rule` with the pattern and `aws events put-targets --rule orders-api-source --targets Id=pipeline,Arn=$PIPELINE_ARN,RoleArn=$EVENTS_ROLE`."
---

Up to now, every change was made by running a script by hand. That works
for one person, once. With a team, someone forgets to run the tests, builds
from a laptop with different library versions, or deploys the wrong branch.
**CI/CD** (continuous integration and continuous delivery) makes every
change go through the same automated steps: build, test, approve, deploy.
A broken change then stops at the step that catches it, not in production.
This lesson builds that pipeline for a small orders application.

```text
 s3://lb-pipeline-artifacts/source/orders-api.zip   (versioned bucket, SSE-KMS with alias/pipeline)
      │ written ──> S3 "Object Created" event ──> EventBridge rule orders-api-source
      ▼                                             │ starts (role events-orders-api)
 pipeline orders-api ◀──────────────────────────────┘
   Source   ── S3 action reads the zip                    ──> artifact SourceOutput
   Build    ── CodeBuild orders-api-build runs buildspec ──> artifact BuildOutput (template.yaml)
               pytest -> reports/junit.xml -> report group unit-tests
   Approve  ── a person clicks Approve or Reject
   Deploy   ── CloudFormation (as role cfn-deploy) creates or updates stack orders-api
```

## The services

| Service | Job | Like |
|---|---|---|
| **CodePipeline** | the **stages** and the order they run in; passes **artifacts** between them | the conveyor belt |
| **CodeBuild** | runs build and test commands in a fresh container, described by a **buildspec** | a clean build machine, per run |
| **CodeDeploy** | rolls new versions out to EC2, Lambda or ECS gradually (next lesson) | |
| CloudFormation, ECS, S3... | deploy targets a pipeline action can call directly | |

An **artifact** is a zip file a stage produces, stored in the pipeline's
**artifact bucket** and referred to **by name** (`SourceOutput`,
`BuildOutput`). An action lists the artifacts it reads (`inputArtifacts`)
and writes (`outputArtifacts`); that is how the build gets the source, and
the deploy gets the build's output.

## The buildspec

`buildspec.yml` sits at the root of the source, next to the code, so the
build instructions are versioned with what they build. It is YAML (spaces,
never tabs):

```yaml
version: 0.2

env:
  secrets-manager:
    SONAR_TOKEN: ci/sonar-token        # a secret's name (or ARN), fetched at build time

phases:
  install:
    runtime-versions:
      python: "3.12"                   # quoted: unquoted 3.10 would become the number 3.1
    commands:
      - pip install pytest
  build:
    commands:
      - python -m pytest --junitxml=reports/junit.xml

reports:
  unit-tests:                          # the report group's name
    files: [junit.xml]
    base-directory: reports
    file-format: JUNITXML

artifacts:
  files: [template.yaml]               # what the next stage receives
```

- **Phases** run in order: `install` (tools), `pre_build` (logins,
  checks), `build`, `post_build` (packaging, pushing). Each is a list of
  shell commands; a command that exits non-zero **fails** the phase, and
  the build. If `build` fails, `post_build` still runs, so it can clean up
  or report.
- **`env`**: `variables` for plain values, `parameter-store` and
  **`secrets-manager`** for values fetched when the build starts. Fetched
  values are **masked** in the build log, and the token never sits in the
  repository. ❗ A plain `variables` entry is stored in the clear, in the
  buildspec and in the build's settings: never put a token there.
- **`reports`**: CodeBuild reads JUnit (or Cucumber, TestNG, coverage)
  files and keeps a **report group** with each run's passes and failures,
  so a failing test shows by name, with history.
- **`artifacts`**: the files handed to the next stage. A file left out is
  simply not there for the deploy.

CodeBuild also sets variables of its own, such as
`CODEBUILD_RESOLVED_SOURCE_VERSION` (the commit or object version being
built), handy as an image tag.

## The project

A **CodeBuild project** says how to run builds:

- **Image**: a managed one, such as `aws/codebuild/standard:7.0` (Ubuntu,
  with many runtime versions), or your own. Building Docker images needs
  **privileged mode** on.
- **Compute type**: `BUILD_GENERAL1_SMALL` (3 GB, 2 vCPUs) up to `LARGE`
  and beyond; 💸 billed per minute of build time.
- A **timeout** (here 20 minutes), so a hung build does not run, and bill,
  for the default hour.
- A **service role** that builds use. Give it only what the build does:

  | Needs | Why |
  |---|---|
  | `logs:CreateLogGroup`, `CreateLogStream`, `PutLogEvents` on `/aws/codebuild/orders-api-build*` | build logs go to CloudWatch Logs |
  | `s3:GetObject`, `s3:PutObject` on the artifact bucket's objects | read the source, write the output |
  | `secretsmanager:GetSecretValue` on the one secret | `SONAR_TOKEN` |
  | `kms:Decrypt`, `kms:GenerateDataKey` on the bucket's key | the artifacts are encrypted with it |

In a pipeline, a project usually has source type `CODEPIPELINE`: the
pipeline hands it the input artifact. The emulator insists on a location,
so this project names the S3 bundle directly, the same object the
pipeline's source stage reads.

## The pipeline

A pipeline is a list of **stages**; each holds one or more **actions**
(several in one stage run in parallel). An action has a category (Source,
Build, Test, Approval, Deploy, Invoke), a **provider**, and a configuration:

| Stage | Provider | Configuration |
|---|---|---|
| **Source** | `S3` | `S3Bucket`, `S3ObjectKey`, `PollForSourceChanges: "false"` |
| **Build** | `CodeBuild` | `ProjectName` |
| **Approve** | `Manual` (category Approval) | optional `CustomData`, a note for the approver |
| **Deploy** | `CloudFormation` | `ActionMode: CREATE_UPDATE`, `StackName`, `TemplatePath`, `RoleArn` |

- **Source**: an S3 source requires a **versioned** bucket: each run
  records which object version it built. Git sources (GitHub, GitLab,
  Bitbucket) connect through **CodeConnections**.
- **Approval**: the run pauses until someone with
  `codepipeline:PutApprovalResult` approves or rejects it, and fails if
  nobody does within 7 days. It can notify an SNS topic.
- **Deploy**: `TemplatePath` is `ARTIFACT::FILE`, here
  `BuildOutput::template.yaml`. `RoleArn` is a role **CloudFormation**
  assumes to create the stack's resources. The pipeline role then only
  needs to pass that role (`iam:PassRole`), not permission to create every
  resource itself. `CREATE_UPDATE` creates the stack, or updates it if it
  exists; the `CHANGE_SET_REPLACE` and `CHANGE_SET_EXECUTE` modes show the
  changes before applying them (Operations lesson 3).

The **artifact store** is the S3 bucket where artifacts live, encrypted
with a **customer managed** KMS key. That matters for pipelines that deploy
into **other accounts**: an AWS managed key's policy cannot be changed, so
other accounts can never decrypt artifacts encrypted with it.

A new pipeline **runs once straight away**; after that it runs on its
triggers. 💸 V2 pipelines (the current type) are billed per action
execution minute; the older V1 type at $1 a month per active pipeline.

## Starting it on change

By default an S3 source **polls** the bucket for changes: slow, and a
legacy method. The recommended way is events:

1. the bucket sends its events to **EventBridge**
   (`put-bucket-notification-configuration` with
   `{"EventBridgeConfiguration": {}}`);
2. a rule matches `Object Created` for this bucket and key:

   ```json
   {"source": ["aws.s3"], "detail-type": ["Object Created"],
    "detail": {"bucket": {"name": ["lb-pipeline-artifacts"]},
               "object": {"key": ["source/orders-api.zip"]}}}
   ```

3. its target is the pipeline's ARN, with a role EventBridge assumes that
   may only `codepipeline:StartPipelineExecution` on it;
4. the source action sets `PollForSourceChanges` to `"false"` (a string),
   so a change does not start the pipeline twice.

## Your task

Done for you: the secret `ci/sonar-token`, and the application files
`app.py`, `test_app.py` and `template.yaml` (which makes an SQS queue).

1. **`buildspec.yml`** (edit the file): version `0.2`; `SONAR_TOKEN` from
   `secrets-manager` `ci/sonar-token` (not a plain variable); Python
   **3.12** under `install`'s `runtime-versions`; a `build` command running
   **pytest** with JUnit XML to **`reports/junit.xml`**; a report group
   **`unit-tests`** in `JUNITXML` format that picks that file up; and
   `template.yaml` in `artifacts`.
2. A KMS key **`alias/pipeline`**, and a bucket **`lb-pipeline-artifacts`**
   with **versioning** on and default encryption **SSE-KMS** with that key.
3. The four files (`buildspec.yml`, `app.py`, `test_app.py`,
   `template.yaml`) zipped **at the top level** of the zip (no folder
   inside), uploaded to **`source/orders-api.zip`** in the bucket.
4. A role **`codebuild-orders-api`** trusted by `codebuild.amazonaws.com`,
   with an inline policy granting the four rows of the table above. The
   check confirms it cannot read other buckets or delete this one.
5. A CodeBuild project **`orders-api-build`**: source type `S3` at
   `lb-pipeline-artifacts/source/orders-api.zip`, artifacts
   `NO_ARTIFACTS`, image `aws/codebuild/standard:7.0`,
   `BUILD_GENERAL1_SMALL`, a **20**-minute timeout, and the role above.
6. Roles **`codepipeline-orders-api`** (trusted by
   `codepipeline.amazonaws.com`) and **`cfn-deploy`** (trusted by
   `cloudformation.amazonaws.com`, with `AmazonSQSFullAccess`).
7. A pipeline **`orders-api`** with the role `codepipeline-orders-api`, its
   artifact store in the bucket encrypted with the key (type `KMS`), and
   exactly four stages, **Source**, **Build**, **Approve**, **Deploy**, in
   that order, **one action each**:
   - Source: S3, the bundle's bucket and key, `PollForSourceChanges`
     `"false"`;
   - Build: CodeBuild `orders-api-build`, taking the Source's output
     artifact;
   - Approve: a manual approval;
   - Deploy: CloudFormation, `CREATE_UPDATE` of the stack **`orders-api`**,
     `TemplatePath` the Build output's `template.yaml`, `RoleArn` the
     `cfn-deploy` role.
8. EventBridge notifications on for the bucket; a role
   **`events-orders-api`** trusted by `events.amazonaws.com`, allowed only
   `codepipeline:StartPipelineExecution` on the pipeline; and a rule
   **`orders-api-source`** with the pattern above, targeting the pipeline
   with that role.

After **Run**:

```
$ aws codepipeline get-pipeline --name orders-api \
    --query 'pipeline.stages[].[name,actions[0].actionTypeId.provider]' --output text
Source	S3
Build	CodeBuild
Approve	Manual
Deploy	CloudFormation
```

The emulator stores the pipeline and the project but runs neither: a
started build stays `IN_PROGRESS` for ever, and `get-pipeline-state` fails.
To try the buildspec's commands, run `python -m pytest
--junitxml=reports/junit.xml` in the terminal.

## Check yourself

1. Why fetch `SONAR_TOKEN` through `secrets-manager` rather than
   `variables`?
   *Plain variables are stored in the clear; fetched secrets stay out of
   the repository and are masked in the logs.*
2. The deploy stage fails with "file not found: template.yaml". Where do
   you look?
   *The buildspec's `artifacts`: only the files listed there reach the
   next stage.*
3. Why does the Deploy action pass a role to CloudFormation?
   *So that CloudFormation creates the resources with that role's
   permissions, and the pipeline role does not need them all.*
4. What does an S3 source need from its bucket?
   *Versioning.*
5. Why `PollForSourceChanges: "false"` when there is an EventBridge rule?
   *Otherwise polling and the rule would both start the pipeline.*
