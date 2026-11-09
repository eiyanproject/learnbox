#!/usr/bin/env bash
# Databases 1: RDS done right.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
# Done for you: the application's security group.
APP_SG=$(aws ec2 create-security-group --group-name app --description "application" \
  --vpc-id "$VPC_ID" --query GroupId --output text)

# 1. Security group db: 5432 only from app.


# 2. DB subnet group app-db: private-a and private-b.


# 3. PostgreSQL app-db: db.t3.micro, 20 GiB gp3, Multi-AZ, encrypted, 7 days of
#    backups, deletion protection, not public, managed master password.


# 4. Read replica app-db-reports.

