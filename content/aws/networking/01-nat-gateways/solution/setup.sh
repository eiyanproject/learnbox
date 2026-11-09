#!/usr/bin/env bash
# Networking 1: NAT gateways, one per AZ.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. A NAT gateway in public-a and one in public-b, each with an Elastic IP.
nat() {  # public-subnet -> NAT gateway ID
  local eip
  eip=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
  aws ec2 create-nat-gateway --subnet-id "$1" --allocation-id "$eip" \
    --query NatGateway.NatGatewayId --output text
}
NAT_A=$(nat "$PUBLIC_A")
NAT_B=$(nat "$PUBLIC_B")

# 2 and 3. A private route table per AZ, through that AZ's NAT gateway.
private_rt() {  # name nat subnet
  local rt
  rt=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$1}]" \
    --query RouteTable.RouteTableId --output text)
  aws ec2 create-route --route-table-id "$rt" \
    --destination-cidr-block 0.0.0.0/0 --nat-gateway-id "$2"
  aws ec2 associate-route-table --route-table-id "$rt" --subnet-id "$3"
}
private_rt private-a "$NAT_A" "$PRIVATE_A"
private_rt private-b "$NAT_B" "$PRIVATE_B"
