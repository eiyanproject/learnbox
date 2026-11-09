#!/usr/bin/env bash
# Lesson 7: a VPC from scratch.
set -euo pipefail

name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }

# 1. The VPC lb-vpc, 10.0.0.0/16. Keep its ID: VPC_ID=$(aws ec2 create-vpc ...)
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications "$(name vpc lb-vpc)" --query Vpc.VpcId --output text)

# 2. Four subnets: public-a 10.0.1.0/24 and private-a 10.0.11.0/24 in us-east-1a,
#    public-b 10.0.2.0/24 and private-b 10.0.12.0/24 in us-east-1b.
subnet() {  # name cidr az
  aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "$2" --availability-zone "$3" \
    --tag-specifications "$(name subnet "$1")" --query Subnet.SubnetId --output text
}
PUBLIC_A=$(subnet public-a 10.0.1.0/24 us-east-1a)
PUBLIC_B=$(subnet public-b 10.0.2.0/24 us-east-1b)
subnet private-a 10.0.11.0/24 us-east-1a
subnet private-b 10.0.12.0/24 us-east-1b

# 3. An internet gateway, attached to the VPC.
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "$(name internet-gateway lb-igw)" \
  --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"

# 4. A route table named public: 0.0.0.0/0 to the internet gateway,
#    associated with public-a and public-b.
RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications "$(name route-table public)" \
  --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id "$RT_ID" \
  --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID"
for s in "$PUBLIC_A" "$PUBLIC_B"; do
  aws ec2 associate-route-table --route-table-id "$RT_ID" --subnet-id "$s"
done

# 5. Public IPs on launch, for the public subnets only.
for s in "$PUBLIC_A" "$PUBLIC_B"; do
  aws ec2 modify-subnet-attribute --subnet-id "$s" --map-public-ip-on-launch
done
