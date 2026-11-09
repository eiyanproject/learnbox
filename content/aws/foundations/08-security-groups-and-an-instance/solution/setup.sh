#!/usr/bin/env bash
# Lesson 8: security groups and an instance.
set -euo pipefail

name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }

# ---- Done for you ----
# The VPC from lesson 7 (sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B)
# and the web-server role and instance profile from lesson 4.
# `awslab given vpc --show` prints the CLI commands they stand for.
eval "$(awslab given vpc)"
eval "$(awslab given web-server-role)"

# ---- This lesson ----

# 1. Security group web: 443 from anywhere, 22 only from 203.0.113.0/24.
WEB_SG=$(aws ec2 create-security-group --group-name web --description "web tier" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$WEB_SG" \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id "$WEB_SG" \
  --protocol tcp --port 22 --cidr 203.0.113.0/24

# 2. Security group db: 5432 only from the web group.
DB_SG=$(aws ec2 create-security-group --group-name db --description "database tier" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$DB_SG" \
  --protocol tcp --port 5432 --source-group "$WEB_SG"

# 3. The instance web: latest Amazon Linux 2023 (Parameter Store), t3.micro,
#    public-a, group web, instance profile web-server, IMDSv2 required.
AMI_ID=$(aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].Value' --output text)
aws ec2 run-instances --image-id "$AMI_ID" --instance-type t3.micro \
  --subnet-id "$PUBLIC_A" --security-group-ids "$WEB_SG" \
  --iam-instance-profile Name=web-server \
  --metadata-options HttpTokens=required \
  --tag-specifications "$(name instance web)" \
  --query 'Instances[0].InstanceId' --output text
