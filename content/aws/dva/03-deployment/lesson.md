---
title: "Domain 3: Deployment"
summary: 24% of the exam. Packaging, testing and shipping code - SAM and CloudFormation, Lambda versions and aliases, API Gateway stages, CodePipeline, CodeBuild and CodeDeploy, and the deployment strategies that make rollback easy.
order: 3
kind: quiz
---

**Weight: 24% of the scored questions.** Four tasks: preparing artifacts,
testing in development environments, automating deployment testing, and
deploying with CI/CD.

## Packaging

- Lambda: **.zip** (50 MB zipped direct upload, 250 MB unzipped including
  layers) or a **container image** (up to 10 GB, from ECR). **Layers** for
  shared dependencies.
- **AWS SAM**: a CloudFormation extension (`AWS::Serverless::Function`,
  `Api`, `SimpleTable`); `sam build`, `sam deploy`, `sam local invoke` and
  `sam local start-api` for testing on a laptop, `sam sync` for fast loops.
- Per-environment configuration: Parameter Store paths, **AWS AppConfig**
  (feature flags with validators and gradual rollout), stage variables.

## Versions, aliases and stages

- A Lambda **version** is an immutable snapshot (`$LATEST` is the mutable
  one). An **alias** (`prod`, `beta`) points at a version - and can split
  traffic between two versions by weight.
- API Gateway **stages** (`dev`, `prod`) are deployments of an API; **stage
  variables** can point a stage at a Lambda alias; stages support **canary**
  settings.

## CI/CD

- **CodePipeline** orchestrates stages (source, build, test, deploy,
  **manual approval**). **CodeBuild** runs a `buildspec.yml` (phases
  install, pre_build, build, post_build; artifacts; reports).
- **CodeDeploy** deploys to EC2/on-premises (in-place or blue/green, driven by
  `appspec.yml` and lifecycle hooks), to **Lambda** (traffic shifting:
  **Canary**, **Linear**, **AllAtOnce**) and to **ECS** (blue/green). CloudWatch
  alarms can trigger automatic **rollback**.
- **Elastic Beanstalk** deployment policies: all at once, rolling, rolling
  with additional batch, **immutable**, traffic splitting.

| Strategy | Downtime | Rollback | Extra capacity |
|---|---|---|---|
| All at once | yes | redeploy | none |
| Rolling | no, reduced capacity | redeploy | none |
| Blue/green, immutable | no | switch back | double, briefly |
| Canary / linear | no | shift back | small |

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 3; AWS service documentation.
