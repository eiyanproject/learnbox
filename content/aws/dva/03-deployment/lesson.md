---
title: "Domain 3: Deployment"
summary: 24% of the exam. Packaging, testing and shipping code - SAM and CloudFormation, Lambda versions and aliases, API Gateway stages, CodePipeline, CodeBuild and CodeDeploy, and the deployment strategies that make rollback easy.
order: 3
kind: quiz
---

Deployment is getting code from a laptop into production safely, again and
again: packaging it, testing it, shipping it through a pipeline, and being
able to go back when a release is bad. The exam focuses on Lambda versions
and aliases, API Gateway stages, SAM, the Code* services, and the
deployment strategies of each.

**Weight: 24% of the scored questions.** Four tasks: preparing artifacts,
testing in development environments, automating deployment testing, and
deploying with CI/CD.

## Packaging

*Practised in Serverless lesson 3, Operations lesson 3.*

- Lambda code is a **.zip** (50 MB zipped for direct upload, 250 MB
  unzipped including layers; larger zips go through S3) or a **container
  image** (up to 10 GB, from ECR). **Layers** carry shared dependencies.
- **AWS SAM** (Serverless Application Model) is a CloudFormation extension:
  a template with `Transform: AWS::Serverless-2016-10-31` can use short
  resource types (`AWS::Serverless::Function`, `Api`, `SimpleTable`) that
  expand into the full CloudFormation resources. Its CLI:

  | Command | Does |
  |---|---|
  | `sam build` | installs dependencies, prepares artifacts |
  | `sam deploy` | uploads them and deploys the stack (`--guided` asks the settings once) |
  | `sam local invoke`, `sam local start-api` | runs the function or API on your machine, in Docker |
  | `sam sync` | pushes code changes to a development stack in seconds |

- **CloudFormation** `package` uploads local code to S3 and rewrites the
  template to point at it.
- **Configuration per environment**: Parameter Store paths
  (`/app/dev/...`, `/app/prod/...`), **AWS AppConfig** (feature flags and
  settings, with validators and gradual rollout, changed without a deploy),
  and API Gateway **stage variables**.

## Versions, aliases and stages

*Practised in CI/CD lesson 2.*

- A Lambda **version** is an immutable, numbered snapshot of code and
  configuration; `$LATEST` is the editable one. An **alias** (`prod`,
  `beta`) is a named pointer to a version, with its own ARN, and can
  **split traffic** between two versions by weight. Callers and triggers
  use the alias, so a release or a rollback is moving the pointer.
- API Gateway **stages** (`dev`, `prod`) are named deployments of an API,
  each with its own URL and settings. **Stage variables** are per-stage
  values, for example pointing the `prod` stage at the `prod` alias of a
  function. Stages support **canary** settings: a percentage of requests
  goes to a new deployment.

## CI/CD

*Practised in CI/CD lessons 1-2.*

- **CodePipeline** orchestrates stages (source, build, test, deploy,
  **manual approval**) and passes **artifacts** between them.
- **CodeBuild** runs `buildspec.yml`: phases `install`, `pre_build`,
  `build`, `post_build`; `env` with secrets from Secrets Manager or
  Parameter Store; `artifacts`; `reports` for test results.
- **CodeDeploy** deploys to:

  | Target | How | Defined by |
  |---|---|---|
  | EC2 / on-premises | in-place or blue/green; lifecycle hooks run scripts (`BeforeInstall`, `AfterInstall`, `ApplicationStart`, `ValidateService`) | `appspec.yml` with files and hooks, an agent on each instance |
  | **Lambda** | traffic shifting on an alias: **Canary**, **Linear**, **AllAtOnce** | AppSpec with versions and hooks (`BeforeAllowTraffic`, `AfterAllowTraffic`) |
  | **ECS** | blue/green with a test listener | AppSpec with the task definition |

  **CloudWatch alarms** on a deployment group trigger automatic
  **rollback**.
- **Elastic Beanstalk** runs web applications with little setup; its
  deployment policies are **all at once**, **rolling**, **rolling with
  additional batch**, **immutable** (a new Auto Scaling group, then swap)
  and **traffic splitting** (canary).

## Choosing a deployment strategy

| Strategy | Downtime | Rollback | Extra capacity |
|---|---|---|---|
| All at once | yes | redeploy the old version | none |
| Rolling | no, but reduced capacity during it | redeploy | none |
| Rolling with additional batch | no, full capacity | redeploy | one batch |
| **Blue/green**, immutable | no | switch back | double, briefly |
| **Canary** / linear | no | shift traffic back | small |

| In a question | Answer |
|---|---|
| "test the new Lambda version on 10% of traffic" | alias weights, or CodeDeploy canary |
| "roll back automatically when errors rise" | CodeDeploy with a CloudWatch alarm |
| "test locally before deploying" | `sam local invoke` / `start-api` |
| "change feature flags without redeploying" | AWS AppConfig |
| "fastest deployment, downtime acceptable" | all at once |
| "no reduced capacity, quickest rollback" | blue/green or immutable |

## Traps

- **`$LATEST`** is not a version you can safely point production at.
- An API change is live only after a **deployment** to a stage.
- **Rolling** reduces capacity during the deployment; rolling **with
  additional batch** does not.
- Lambda deployments in CodeDeploy are always **blue/green** (traffic
  shifting), never in-place.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 3; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
