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
PCX=$(aws ec2 create-vpc-peering-connection --vpc-id "$VPC_ID" --peer-vpc-id "$DATA_VPC" \
  --query VpcPeeringConnection.VpcPeeringConnectionId --output text)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id "$PCX" >/dev/null

# 2. Routes both ways: private -> 10.1.0.0/16, data -> 10.0.0.0/16.
aws ec2 create-route --route-table-id "$PRIVATE_RT" \
  --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id "$PCX"
aws ec2 create-route --route-table-id "$DATA_RT" \
  --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id "$PCX"

# 3. DNS hostnames on for both VPCs.
for v in "$VPC_ID" "$DATA_VPC"; do
  aws ec2 modify-vpc-attribute --vpc-id "$v" --enable-dns-hostnames '{"Value":true}'
done

# 4. Private hosted zone internal.example for both VPCs, with
#    db.internal.example -> 10.1.11.10.
ZONE=$(aws route53 create-hosted-zone --name internal.example \
  --caller-reference "lb-$(date +%s)" \
  --vpc "VPCRegion=us-east-1,VPCId=$VPC_ID" \
  --hosted-zone-config PrivateZone=true \
  --query HostedZone.Id --output text)
aws route53 associate-vpc-with-hosted-zone --hosted-zone-id "$ZONE" \
  --vpc "VPCRegion=us-east-1,VPCId=$DATA_VPC" >/dev/null
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "db.internal.example", "Type": "A", "TTL": 60,
      "ResourceRecords": [{"Value": "10.1.11.10"}]
    }
  }]
}' >/dev/null
