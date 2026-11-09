#!/usr/bin/env bash
# Databases 3: a cache that survives an AZ.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
# Done for you: the application's security group.
APP_SG=$(aws ec2 create-security-group --group-name app --description "application" \
  --vpc-id "$VPC_ID" --query GroupId --output text)

# 1. Security group cache: 6379 only from app.
CACHE_SG=$(aws ec2 create-security-group --group-name cache --description "cache" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$CACHE_SG" \
  --protocol tcp --port 6379 --source-group "$APP_SG" >/dev/null

# 2. Cache subnet group cache: private-a and private-b.
aws elasticache create-cache-subnet-group --cache-subnet-group-name cache \
  --cache-subnet-group-description "private subnets" \
  --subnet-ids "$PRIVATE_A" "$PRIVATE_B" >/dev/null

# 3. Replication group sessions: redis, cache.t3.micro, two nodes, automatic
#    failover, Multi-AZ, encrypted at rest and in transit.
aws elasticache create-replication-group --replication-group-id sessions \
  --replication-group-description "user sessions" \
  --engine redis --cache-node-type cache.t3.micro --num-cache-clusters 2 \
  --automatic-failover-enabled --multi-az-enabled \
  --at-rest-encryption-enabled --transit-encryption-enabled \
  --cache-subnet-group-name cache --security-group-ids "$CACHE_SG" \
  --query ReplicationGroup.Status --output text
