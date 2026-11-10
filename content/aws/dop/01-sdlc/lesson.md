---
title: "Domain 1: SDLC automation"
summary: 22% of the exam, the largest domain. CI/CD pipelines, automated testing, building and managing artifacts, and deployment strategies for instances, containers and serverless.
order: 1
kind: quiz
---

**Weight: 22% of the scored questions.**

## Pipelines

- **CodePipeline** stages and actions (source, build, test, approval,
  deploy), cross-account and cross-Region actions (artifact buckets with KMS
  keys the other accounts can use), triggers and filters on Git branches and
  tags. Source from **CodeConnections** (GitHub, GitLab, Bitbucket) or S3/ECR.
- **CodeBuild** with buildspec phases, reports for test results, caching,
  VPC access, secrets from Secrets Manager or Parameter Store.
- Artifacts: **CodeArtifact** for packages (upstream repositories, domains),
  **ECR** for images (scanning, lifecycle policies, replication), S3 for
  bundles; sign them (AWS Signer, image signing).

## Deployment strategies

- **CodeDeploy**: EC2/on-premises (in-place or blue/green, AppSpec
  hooks, deployment groups, automatic rollback on alarms), Lambda
  (canary/linear/all-at-once via alias traffic shifting), ECS (blue/green
  with test listener).
- ECS rolling updates with the **deployment circuit breaker**; EKS
  rollouts; Elastic Beanstalk policies (all at once, rolling, rolling with
  additional batch, immutable, traffic splitting, blue/green by URL swap).
- Pick by risk and speed: canary and blue/green give fast rollback;
  immutable avoids mixed fleets.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 1; AWS service documentation.
