---
title: ECR repositories
summary: A private container registry done properly - immutable tags, scanning on push, KMS encryption, lifecycle rules that keep storage in check, a policy that lets another account pull, and replication to a second Region.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws ecr create-repository --repository-name orders-api --image-tag-mutability IMMUTABLE --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS`."
  - "Lifecycle rules are JSON with `rules`, each with `rulePriority`, `selection` and `\"action\": {\"type\": \"expire\"}`. Untagged images: `{\"tagStatus\": \"untagged\", \"countType\": \"sinceImagePushed\", \"countUnit\": \"days\", \"countNumber\": 7}`. Releases: `{\"tagStatus\": \"tagged\", \"tagPrefixList\": [\"release-\"], \"countType\": \"imageCountMoreThan\", \"countNumber\": 20}`."
  - "`aws ecr put-lifecycle-policy --repository-name orders-api --lifecycle-policy-text file://lifecycle.json` and `aws ecr set-repository-policy --repository-name orders-api --policy-text file://repo-policy.json`."
  - "Replication is set for the whole registry: `aws ecr put-replication-configuration --replication-configuration '{\"rules\":[{\"destinations\":[{\"region\":\"eu-west-1\",\"registryId\":\"'$ACCOUNT'\"}]}]}'`."
---

**Amazon ECR** stores container images (and other OCI artifacts) privately,
next to the services that run them. ECS, EKS and Lambda pull from it with
IAM, not passwords.

## A repository's settings

- **Tag immutability.** With `IMMUTABLE`, a tag such as `release-42` can
  never be pushed again with different content, so what was tested is what
  runs. Deploy by immutable tag or by digest (`@sha256:...`), never by
  `latest`.
- **Scanning.** *Basic* scanning checks operating system packages on push.
  *Enhanced* scanning (Amazon Inspector) adds programming-language packages
  and rescans continuously as new CVEs appear.
- **Encryption.** Always on; `KMS` uses a KMS key (the AWS managed
  `aws/ecr` key unless you name your own) instead of the default AES-256.

## Lifecycle policies

Every pushed image is stored until it is deleted, and CI pushes a lot.
Lifecycle rules expire images automatically, evaluated in `rulePriority`
order (lowest first):

- untagged images older than N days (`sinceImagePushed`);
- all but the newest N images matching a tag prefix (`imageCountMoreThan`).

## Sharing

A **repository policy** is a resource policy: it can let another account
(say, production) pull images built in a tooling account, with the pull
actions `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer` and
`ecr:BatchCheckLayerAvailability`. **Replication** copies every new image to
other Regions or accounts, so each Region pulls locally.

## Your task

1. A repository **`orders-api`**: **immutable** tags, **scan on push**,
   encryption type **KMS**.
2. A lifecycle policy with two rules: priority **1** expires **untagged**
   images after **7 days**; priority **2** keeps only the newest **20**
   images tagged **`release-`**.
3. A repository policy, statement id **`ProdPull`**, that lets account
   **`111122223333`** pull - the three pull actions only.
4. Registry replication to **eu-west-1** in your own account.

After **Run**: `aws ecr describe-repositories --repository-names orders-api`.
