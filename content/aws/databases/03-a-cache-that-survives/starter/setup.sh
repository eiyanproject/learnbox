#!/usr/bin/env bash
# Databases 3: a cache that survives an AZ.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
# Done for you: the application's security group.
APP_SG=$(aws ec2 create-security-group --group-name app --description "application" \
  --vpc-id "$VPC_ID" --query GroupId --output text)

# 1. Security group cache: 6379 only from app.


# 2. Cache subnet group cache: private-a and private-b.


# 3. Replication group sessions: redis, cache.t3.micro, two nodes, automatic
#    failover, Multi-AZ, encrypted at rest and in transit.

