#!/usr/bin/env bash
# Lesson 8: security groups and an instance.
set -euo pipefail

name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }

# ---- From lesson 7: the VPC (done for you) ----
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications "$(name vpc lb-vpc)" --query Vpc.VpcId --output text)
subnet() {  # name cidr az
  aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "$2" --availability-zone "$3" \
    --tag-specifications "$(name subnet "$1")" --query Subnet.SubnetId --output text
}
PUBLIC_A=$(subnet public-a 10.0.1.0/24 us-east-1a)
PUBLIC_B=$(subnet public-b 10.0.2.0/24 us-east-1b)
PRIVATE_A=$(subnet private-a 10.0.11.0/24 us-east-1a)
PRIVATE_B=$(subnet private-b 10.0.12.0/24 us-east-1b)
IGW_ID=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications "$(name route-table public)" --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id "$RT_ID" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" >/dev/null
for s in "$PUBLIC_A" "$PUBLIC_B"; do
  aws ec2 associate-route-table --route-table-id "$RT_ID" --subnet-id "$s" >/dev/null
  aws ec2 modify-subnet-attribute --subnet-id "$s" --map-public-ip-on-launch
done

# ---- From lesson 4: the web-server role and instance profile (done for you) ----
aws iam create-role --role-name web-server --assume-role-policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
aws iam attach-role-policy --role-name web-server --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam create-instance-profile --instance-profile-name web-server >/dev/null
aws iam add-role-to-instance-profile --instance-profile-name web-server --role-name web-server

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
