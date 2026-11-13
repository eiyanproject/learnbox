---
title: "Domain 1: SDLC automation"
summary: 22% of the exam, the largest domain. CI/CD pipelines, automated testing, building and managing artifacts, and deployment strategies for instances, containers and serverless.
order: 1
kind: quiz
---

This page reviews the first domain of the **AWS Certified DevOps Engineer
- Professional** exam (DOP-C02), followed by practice questions. DevOps on
AWS means that building, testing, deploying, configuring and recovering
are all **automated**: the questions ask which automation, and how to make
it safe. It builds on the Developer and CloudOps associate pages. Each
section names the hands-on lessons where you built what it describes.

**Weight: 22% of the scored questions**, the largest domain.

## How a Professional question is built

The exam has 75 questions in 180 minutes and passes at 750 of 1000.
Questions are long, and several options work. The right one meets **every**
constraint, and in this exam the usual qualifier is "**most automated**" or
"**least operational overhead**": an option that needs a person to watch,
click or run a script is usually wrong when an automated one exists. Read
the last sentence first, then cross out options that miss any requirement.

## Pipelines

*Practised in CI/CD lesson 1.*

- **CodePipeline**: stages of **actions** (source, build, test, approval,
  deploy, invoke), passing artifacts through an S3 artifact store. Advanced
  points:
  - **Cross-account** deployments: the pipeline assumes a role in the target
    account, and the artifact bucket's **KMS key** must be a customer
    managed key whose policy lets the target accounts decrypt (an AWS
    managed key cannot be shared).
  - **Cross-Region** actions need an artifact bucket in each Region.
  - V2 pipelines have **triggers with filters** on Git branches, tags and
    file paths, and pipeline-level variables.
  - Sources: **CodeConnections** for GitHub, GitLab and Bitbucket; S3; ECR.
- **CodeBuild**: buildspec phases, test **reports**, **caching** (S3 or
  local) to speed up dependency downloads, **VPC access** for builds that
  reach private resources, secrets from Secrets Manager or Parameter Store.
- **Artifacts**:

  | Kind | Store |
  |---|---|
  | language packages (npm, pip, Maven) | **CodeArtifact**: **domains** across accounts, **upstream repositories** proxying public registries |
  | container images | **ECR**: scanning, lifecycle policies, replication |
  | deployment bundles | S3 |

  Sign them so deploys can prove where they came from: **AWS Signer** for
  Lambda code, image signing for containers.

## Deployment strategies

*Practised in Containers lesson 2, CI/CD lesson 2.*

- **CodeDeploy**:

  | Platform | Options | Notes |
  |---|---|---|
  | EC2 / on-premises | **in-place** or **blue/green** | the agent runs AppSpec **lifecycle hooks** (`ApplicationStop`, `BeforeInstall`, `AfterInstall`, `ApplicationStart`, `ValidateService`); deployment groups by tag or Auto Scaling group |
  | Lambda | canary, linear, all at once | traffic shifting on an alias; `BeforeAllowTraffic` and `AfterAllowTraffic` hooks |
  | ECS | blue/green | a **test listener** on the load balancer for checks before traffic moves |

  **Automatic rollback** on deployment failure or on a CloudWatch alarm.
- **ECS rolling updates** with the **deployment circuit breaker** (rollback
  after repeated task failures); ECS's built-in blue/green, canary and
  linear deployments; **EKS** rollouts by Kubernetes Deployments.
- **Elastic Beanstalk** policies: all at once, rolling, rolling with
  additional batch, **immutable** (a new Auto Scaling group), **traffic
  splitting** (canary), and **blue/green by swapping environment URLs**
  (a CNAME swap).

Pick by **risk** and **speed**:

| Need | Strategy |
|---|---|
| fastest rollback | blue/green or canary (shift back) |
| never a mixed fleet of old and new | immutable or blue/green |
| no extra capacity | rolling |
| test on real traffic first | canary |

| In a question | Answer |
|---|---|
| "deploy to the prod account from a tooling account pipeline" | cross-account role + customer managed KMS key on the artifact bucket |
| "builds download the same dependencies every time" | CodeBuild caching, CodeArtifact upstream |
| "roll back automatically when errors rise during a deploy" | CodeDeploy with alarms and auto rollback |
| "an ECS deployment of a broken image never ends" | the deployment circuit breaker with rollback |
| "run validation scripts after the new version starts on EC2" | the `ValidateService` hook |

## Traps

- An AWS managed KMS key cannot be used by other accounts.
- **In-place** deployments are not possible for Lambda or ECS.
- A manual approval is right only when the story asks for a person.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 1; AWS service documentation.

## Questions from open banks

- 4 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
