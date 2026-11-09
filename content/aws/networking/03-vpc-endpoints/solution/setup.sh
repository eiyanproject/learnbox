#!/usr/bin/env bash
# Networking 3: VPC endpoints.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# Done for you: one private route table for both private subnets, and the bucket.
PRIVATE_RT=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private}]' \
  --query RouteTable.RouteTableId --output text)
for s in "$PRIVATE_A" "$PRIVATE_B"; do
  aws ec2 associate-route-table --route-table-id "$PRIVATE_RT" --subnet-id "$s" >/dev/null
done
aws s3api create-bucket --bucket lb-private-data >/dev/null

# 1. endpoint-policy.json (edit the file).

# 2. A gateway endpoint for S3 on PRIVATE_RT, with that policy. Keep its ID.
S3_ENDPOINT=$(aws ec2 create-vpc-endpoint --vpc-id "$VPC_ID" \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids "$PRIVATE_RT" \
  --policy-document file://endpoint-policy.json \
  --query VpcEndpoint.VpcEndpointId --output text)

# 3. Security group endpoints (TCP 443 from 10.0.0.0/16), and an interface
#    endpoint for SSM in both private subnets, private DNS on.
EP_SG=$(aws ec2 create-security-group --group-name endpoints \
  --description "interface endpoints" --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$EP_SG" \
  --protocol tcp --port 443 --cidr 10.0.0.0/16 >/dev/null
aws ec2 create-vpc-endpoint --vpc-id "$VPC_ID" --vpc-endpoint-type Interface \
  --service-name com.amazonaws.us-east-1.ssm \
  --subnet-ids "$PRIVATE_A" "$PRIVATE_B" \
  --security-group-ids "$EP_SG" --private-dns-enabled \
  --query VpcEndpoint.VpcEndpointId --output text

# 4. bucket-policy.json with your endpoint's ID in it, applied to the bucket.
sed "s/VPCE_ID/$S3_ENDPOINT/" bucket-policy.json > bucket-policy.final.json
aws s3api put-bucket-policy --bucket lb-private-data --policy file://bucket-policy.final.json
