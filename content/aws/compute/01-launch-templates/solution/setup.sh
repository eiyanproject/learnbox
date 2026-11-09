#!/usr/bin/env bash
# Compute 1: launch templates and user data.
set -euo pipefail

# Done for you: the VPC, the web-server role, a security group and the AMI.
eval "$(awslab given vpc)"
eval "$(awslab given web-server-role)"
WEB_SG=$(aws ec2 create-security-group --group-name web --description "web tier" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
AMI_ID=$(aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].Value' --output text)

# 1 and 2: edit user-data.sh and template.json. This fills in the IDs:
USER_DATA=$(base64 -w0 user-data.sh)
sed -e "s/AMI_ID/$AMI_ID/" -e "s/WEB_SG/$WEB_SG/" -e "s|USER_DATA|$USER_DATA|" \
  template.json > template.final.json

# 3. The launch template web, from template.final.json.
aws ec2 create-launch-template --launch-template-name web \
  --launch-template-data file://template.final.json \
  --query LaunchTemplate.LaunchTemplateId --output text

# 4. Version 2 with t3.small, made the default.
aws ec2 create-launch-template-version --launch-template-name web \
  --source-version 1 --launch-template-data '{"InstanceType":"t3.small"}' \
  --query LaunchTemplateVersion.VersionNumber --output text
aws ec2 modify-launch-template --launch-template-name web --default-version 2 >/dev/null
