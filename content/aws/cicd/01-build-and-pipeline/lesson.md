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

A pipeline turns "it works on my machine" into "every change is built,
tested and deployed the same way". On AWS the pieces are:

- **CodePipeline** - the stages and the flow of **artifacts** between them,
  stored in an S3 bucket;
- **CodeBuild** - containers that run your build and tests, described by a
  **buildspec**;
- a deploy target: CloudFormation, CodeDeploy, ECS, Elastic Beanstalk, S3.

## The buildspec

`buildspec.yml` lives with the code. Phases run in order - `install`,
`pre_build`, `build`, `post_build` - and a failing command fails the build.
`env` can pull values from **Secrets Manager** or **Parameter Store** at
build time (masked in logs), so tokens never sit in the repository.
`reports` turns JUnit or coverage files into test reports with history, and
`artifacts` lists what the next stage gets.

## The project

A CodeBuild project names the image (`aws/codebuild/standard:7.0`), the
compute size, a timeout, and a **service role**. Give that role only what
the build does: write its logs, read and write the artifact bucket, read
its secret, use the bucket's KMS key.

A project used only from a pipeline usually has source type `CODEPIPELINE`;
the emulator here insists on a location, so this one is given its S3 source
bundle, which is what the pipeline's source stage reads too.

## The pipeline

1. **Source** - here an S3 object (`source/orders-api.zip`) in a
   **versioned** bucket; GitHub, GitLab and Bitbucket come in through
   CodeConnections.
2. **Build** - the CodeBuild project; its output artifact carries
   `template.yaml`.
3. **Approve** - a **manual approval** that waits for a person.
4. **Deploy** - CloudFormation creates or updates the stack, using a role
   that CloudFormation assumes (so the pipeline itself does not need
   permission to create every resource).

The **artifact store** should be encrypted with a customer managed KMS key -
required anyway for cross-account pipelines, because AWS managed keys
cannot be shared.

## Starting it

Polling the source is the old way. Instead, the bucket sends events to
**EventBridge**, and a rule starts the pipeline when the source object is
written, through a role EventBridge assumes.

## Your task

Done for you: the secret `ci/sonar-token`, and the application files
`app.py`, `test_app.py` and `template.yaml`.

1. **`buildspec.yml`** (edit the file): version 0.2; `SONAR_TOKEN` from
   Secrets Manager `ci/sonar-token`; Python **3.12** in `install`; a
   `build` command that runs the tests writing JUnit XML to
   `reports/junit.xml`; a report group **`unit-tests`** for it; and
   `template.yaml` as the artifact.
2. A KMS key **`alias/pipeline`**, and a bucket **`lb-pipeline-artifacts`**
   with **versioning** and default **SSE-KMS** with that key.
3. The four files zipped and uploaded to
   **`source/orders-api.zip`** in that bucket.
4. A role **`codebuild-orders-api`** (trusted by `codebuild.amazonaws.com`)
   with an inline policy allowing logs (`logs:CreateLogGroup`,
   `CreateLogStream`, `PutLogEvents`), `s3:GetObject` and `s3:PutObject` on
   the bucket's objects, `secretsmanager:GetSecretValue` on the secret, and
   `kms:Decrypt` and `kms:GenerateDataKey` on the key.
5. A CodeBuild project **`orders-api-build`**: S3 source from that object,
   no artifacts of its own, `aws/codebuild/standard:7.0`,
   `BUILD_GENERAL1_SMALL`, a **20**-minute timeout, the role above.
6. Roles **`codepipeline-orders-api`** (trusted by
   `codepipeline.amazonaws.com`) and **`cfn-deploy`** (trusted by
   `cloudformation.amazonaws.com`, with `AmazonSQSFullAccess` - the template
   makes a queue).
7. A pipeline **`orders-api`** with the artifact store in the bucket,
   encrypted with the key, and the four stages **Source**, **Build**,
   **Approve**, **Deploy** as described (stack **`orders-api`**).
8. EventBridge notifications on for the bucket, a role
   **`events-orders-api`** (trusted by `events.amazonaws.com`) allowed
   `codepipeline:StartPipelineExecution` on the pipeline, and a rule
   **`orders-api-source`** for S3 **Object Created** events on that object,
   targeting the pipeline with that role.
