#!/usr/bin/env bash
# Databases 1: RDS done right.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
# Done for you: the application's security group.
APP_SG=$(aws ec2 create-security-group --group-name app --description "application" \
  --vpc-id "$VPC_ID" --query GroupId --output text)

# 1. Security group db: 5432 only from app.
DB_SG=$(aws ec2 create-security-group --group-name db --description "database" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$DB_SG" \
  --protocol tcp --port 5432 --source-group "$APP_SG" >/dev/null

# 2. DB subnet group app-db: private-a and private-b.
aws rds create-db-subnet-group --db-subnet-group-name app-db \
  --db-subnet-group-description "app database" \
  --subnet-ids "$PRIVATE_A" "$PRIVATE_B" >/dev/null

# 3. PostgreSQL app-db: db.t3.micro, 20 GiB gp3, Multi-AZ, encrypted, 7 days of
#    backups, deletion protection, not public, managed master password.
aws rds create-db-instance --db-instance-identifier app-db \
  --engine postgres --db-instance-class db.t3.micro \
  --allocated-storage 20 --storage-type gp3 \
  --master-username app --manage-master-user-password \
  --multi-az --storage-encrypted \
  --backup-retention-period 7 --deletion-protection \
  --no-publicly-accessible \
  --db-subnet-group-name app-db --vpc-security-group-ids "$DB_SG" \
  --query DBInstance.DBInstanceStatus --output text

# 4. Read replica app-db-reports.
aws rds create-db-instance-read-replica --db-instance-identifier app-db-reports \
  --source-db-instance-identifier app-db --db-instance-class db.t3.micro \
  --query DBInstance.DBInstanceStatus --output text
