#!/usr/bin/env bash
# Networking 4: peering and private DNS.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# Done for you: lb-vpc's private route table, and the data VPC.
PRIVATE_RT=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private}]' \
  --query RouteTable.RouteTableId --output text)
for s in "$PRIVATE_A" "$PRIVATE_B"; do
  aws ec2 associate-route-table --route-table-id "$PRIVATE_RT" --subnet-id "$s" >/dev/null
done
DATA_VPC=$(aws ec2 create-vpc --cidr-block 10.1.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=data-vpc}]' \
  --query Vpc.VpcId --output text)
DATA_A=$(aws ec2 create-subnet --vpc-id "$DATA_VPC" --cidr-block 10.1.11.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=data-a}]' \
  --query Subnet.SubnetId --output text)
DATA_RT=$(aws ec2 create-route-table --vpc-id "$DATA_VPC" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=data}]' \
  --query RouteTable.RouteTableId --output text)
aws ec2 associate-route-table --route-table-id "$DATA_RT" --subnet-id "$DATA_A" >/dev/null

# 1. A peering connection between lb-vpc and data-vpc, accepted.


# 2. Routes both ways: private -> 10.1.0.0/16, data -> 10.0.0.0/16.


# 3. DNS hostnames on for both VPCs.


# 4. Private hosted zone internal.example for both VPCs, with
#    db.internal.example -> 10.1.11.10.

