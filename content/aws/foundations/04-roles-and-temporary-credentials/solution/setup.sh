#!/usr/bin/env bash
# Lesson 4: roles and temporary credentials.
set -euo pipefail

# 1. The web-server role (trusting EC2, from ec2-trust.json), with
#    AmazonS3ReadOnlyAccess, and an instance profile web-server holding it.
aws iam create-role --role-name web-server \
  --assume-role-policy-document file://ec2-trust.json
aws iam attach-role-policy --role-name web-server \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam create-instance-profile --instance-profile-name web-server
aws iam add-role-to-instance-profile --instance-profile-name web-server \
  --role-name web-server

# 2. The auditor role (trusting account 111122223333 with the external ID,
#    from auditor-trust.json), with SecurityAudit.
aws iam create-role --role-name auditor \
  --assume-role-policy-document file://auditor-trust.json
aws iam attach-role-policy --role-name auditor \
  --policy-arn arn:aws:iam::aws:policy/SecurityAudit
