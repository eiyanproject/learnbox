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


# 3. Security group endpoints (TCP 443 from 10.0.0.0/16), and an interface
#    endpoint for SSM in both private subnets, private DNS on.


# 4. bucket-policy.json with your endpoint's ID in it, applied to the bucket.

