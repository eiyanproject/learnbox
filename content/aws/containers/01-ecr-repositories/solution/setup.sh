#!/usr/bin/env bash
# Containers 1: ECR repositories.
set -euo pipefail

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# 1. orders-api: immutable tags, scan on push, KMS encryption.
aws ecr create-repository --repository-name orders-api \
  --image-tag-mutability IMMUTABLE \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS >/dev/null

# 2. Lifecycle: (1) untagged after 7 days, (2) keep 20 release- images.
cat > lifecycle.json <<'EOF'
{
  "rules": [
    {"rulePriority": 1, "description": "untagged after 7 days",
     "selection": {"tagStatus": "untagged", "countType": "sinceImagePushed",
                   "countUnit": "days", "countNumber": 7},
     "action": {"type": "expire"}},
    {"rulePriority": 2, "description": "keep the newest 20 releases",
     "selection": {"tagStatus": "tagged", "tagPrefixList": ["release-"],
                   "countType": "imageCountMoreThan", "countNumber": 20},
     "action": {"type": "expire"}}
  ]
}
EOF
aws ecr put-lifecycle-policy --repository-name orders-api \
  --lifecycle-policy-text file://lifecycle.json >/dev/null

# 3. Repository policy ProdPull: account 111122223333 may pull.
cat > repo-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ProdPull",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
    "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer",
               "ecr:BatchCheckLayerAvailability"]
  }]
}
EOF
aws ecr set-repository-policy --repository-name orders-api \
  --policy-text file://repo-policy.json >/dev/null

# 4. Replicate the registry to eu-west-1 in this account.
aws ecr put-replication-configuration --replication-configuration \
  "{\"rules\":[{\"destinations\":[{\"region\":\"eu-west-1\",\"registryId\":\"$ACCOUNT\"}]}]}" >/dev/null
