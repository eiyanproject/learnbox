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

A **container image** is an application packed with everything it needs to
run: its code, the language runtime, the libraries and a minimal operating
system layer. Build it once, and it runs the same on a laptop, in CI and in
production. Images need somewhere to live between being built and being run:
a **registry**. Docker Hub is a public one; **Amazon ECR** (Elastic Container
Registry) is AWS's private one, next to the services that run the images.
ECS, EKS and Lambda pull from it with their **IAM roles**, so no registry
password is stored anywhere.

```text
 CI build ──docker push──> ECR: 123456789012.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-42
                              │  scan on push, lifecycle rules, KMS encryption
                              ├──replicate──> ECR in eu-west-1 (same images, pulled locally there)
                              └──pull (repository policy)──> production account 111122223333
```

## Words first

- A **registry** is one per account per Region:
  `ACCOUNT.dkr.ecr.REGION.amazonaws.com`.
- A **repository** holds the versions of one image, such as `orders-api`.
- An image is named `registry/repository:tag`. A **tag** (`release-42`,
  `latest`) is a human label that points at an image; the **digest**
  (`sha256:e3b0...`) is a hash of the image's content, and so names exactly
  one image forever.
- An image is made of **layers**, stored once and shared between images that
  have them in common. ECR keeps layers in S3, which is why pulls through a
  VPC endpoint also need the S3 gateway endpoint (Networking lesson 3).

Pushing from a laptop or CI first signs Docker in with a 12-hour token
from IAM:

```
aws ecr get-login-password | docker login --username AWS --password-stdin \
  ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag orders-api:build ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-42
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-42
```

(The sandbox has no Docker, so this lesson configures the repository only.)

## A repository's settings

- **Tag immutability.** By default tags are **mutable**: pushing
  `release-42` again silently moves the tag to the new image, and what was
  tested is no longer what runs. With `IMMUTABLE`, a second push of the same
  tag with different content fails with `ImageTagAlreadyExistsException`.
  Deploy by an immutable tag or by digest (`@sha256:...`), never by
  `latest`, which by definition keeps moving.
- **Scanning** looks for known vulnerabilities (CVEs) in the image:

  | | **Basic** | **Enhanced** (Amazon Inspector) |
  |---|---|---|
  | What it checks | operating system packages | OS packages **and** language packages (pip, npm, Maven...) |
  | When | on push, or on demand | on push, then **continuously** as new CVEs are published |
  | 💸 Cost | free | billed per image scanned by Inspector |

  `scanOnPush=true` turns basic scanning on for the repository; results come
  from `describe-image-scan-findings`.
- **Encryption** is always on. The default is AES-256 with keys AWS manages;
  `KMS` uses a KMS key instead (the AWS managed `aws/ecr` key unless you
  name your own), so key use is logged in CloudTrail and controlled by a key
  policy (Security lesson 1). ❗ Encryption, like the repository's name, is
  chosen at creation and **cannot be changed** later.

The emulator's view of the repository after **Run**:

```
$ aws ecr describe-repositories --repository-names orders-api \
    --query 'repositories[0].[repositoryUri,imageTagMutability,imageScanningConfiguration.scanOnPush,encryptionConfiguration.encryptionType]'
[
    "123456789012.dkr.ecr.us-east-1.amazonaws.com/orders-api",
    "IMMUTABLE",
    true,
    "KMS"
]
```

## Lifecycle policies: keeping storage in check

Every pushed image is stored, and billed (💸 about $0.10 per GB a month),
until someone deletes it. CI pushes on every commit, so a busy repository
grows by hundreds of images a month. A **lifecycle policy** deletes
("expires") images automatically. It is a list of **rules**, each with:

- a `rulePriority`: rules are evaluated from the **lowest** number up, and
  an image is handled by the first rule that selects it;
- a `selection`: which images (`tagStatus` `untagged`, `tagged` with a
  `tagPrefixList`, or `any`) and how to count them:
  - `sinceImagePushed` with `countUnit: days`: images older than N days;
  - `imageCountMoreThan`: all but the **newest** N images;
- an `action`, which is always `{"type": "expire"}`.

```json
{"rulePriority": 2, "description": "keep the newest 20 releases",
 "selection": {"tagStatus": "tagged", "tagPrefixList": ["release-"],
               "countType": "imageCountMoreThan", "countNumber": 20},
 "action": {"type": "expire"}}
```

**Untagged** images appear when a mutable tag moves on, or when a build
pushes layers without a tag; nothing refers to them, so they are the safest
to expire. Expiry is not instant: AWS applies the rules within about a day.
`start-lifecycle-policy-preview` shows what a policy would delete before it
deletes anything.

## Sharing across accounts and Regions

A **repository policy** is a resource policy (Foundations lesson 3), like a
bucket policy. The common case: images are built once in a tooling account,
and the production account pulls them. A pull uses three actions:

| Action | What it does |
|---|---|
| `ecr:BatchCheckLayerAvailability` | asks which layers exist |
| `ecr:GetDownloadUrlForLayer` | gets an S3 download URL for each layer |
| `ecr:BatchGetImage` | gets the image manifest (the list of layers) |

Grant exactly those to the other account, and it can pull but never push or
delete. Its roles still need the same actions in their **own** IAM policies,
plus `ecr:GetAuthorizationToken` (which is account-wide, never in a
repository policy): as always across accounts, both sides must allow.

**Replication** copies every image pushed from now on to other Regions or
accounts. It is configured for the **whole registry**, not per repository
(a rule can narrow it with repository filters), and does not copy images
that were already there. A service in eu-west-1 then pulls from its own
Region: faster, with no cross-Region data charges at each start, and still
working if us-east-1 has a problem.

## Your task

1. A repository **`orders-api`**: **immutable** tags, **scan on push**,
   encryption type **KMS**.
2. A lifecycle policy with two rules, each with `"action": {"type":
   "expire"}`:
   - priority **1** expires **untagged** images **7 days** after they are
     pushed (`sinceImagePushed`, `days`);
   - priority **2** keeps only the newest **20** images whose tag starts
     with **`release-`** (`tagged`, `tagPrefixList ["release-"]`,
     `imageCountMoreThan`).
3. A repository policy whose statement has the Sid **`ProdPull`**, allowing
   account **`111122223333`** exactly the three pull actions above, and
   nothing else.
4. Registry replication to **eu-west-1**, with your own account as the
   destination registry.

After **Run**:

```
aws ecr describe-repositories --repository-names orders-api
aws ecr get-lifecycle-policy --repository-name orders-api --query lifecyclePolicyText --output text
aws ecr describe-registry --query replicationConfiguration
```

## Check yourself

1. A deploy uses `orders-api:latest`. Why is that a problem?
   *`latest` moves with every push, so two tasks started a minute apart can
   run different code, and a rollback cannot name the old version.*
2. What does `IMMUTABLE` change for a CI pipeline?
   *Every build must push a new tag (a version or commit ID); pushing an
   existing tag fails.*
3. Which scanning finds a vulnerable npm package published as a CVE last
   week, in an image pushed last month?
   *Enhanced scanning: it covers language packages and rescans continuously.*
4. The production account's role gets `AccessDenied` pulling, although the
   repository policy allows it. What is missing?
   *The role's own IAM policy: it needs the pull actions and
   `ecr:GetAuthorizationToken` too.*
5. Two lifecycle rules both select an image. Which applies?
   *The one with the lower `rulePriority`.*
