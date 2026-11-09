#!/usr/bin/env bash
# Networking 2: network ACLs that deny.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. A network ACL named public.
ACL=$(aws ec2 create-network-acl --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=public}]' \
  --query NetworkAcl.NetworkAclId --output text)

rule() {  # direction number protocol ports cidr action
  local ports=()
  [ "$4" != "-" ] && ports=(--port-range "From=${4%-*},To=${4#*-}")
  aws ec2 create-network-acl-entry --network-acl-id "$ACL" "--$1" \
    --rule-number "$2" --protocol "$3" "${ports[@]}" \
    --cidr-block "$5" --rule-action "$6"
}

# 2. Its inbound rules.
rule ingress 90  -1  -          198.51.100.0/24 deny
rule ingress 100 tcp 443-443    0.0.0.0/0       allow
rule ingress 110 tcp 22-22      203.0.113.0/24  allow
rule ingress 120 tcp 1024-65535 0.0.0.0/0       allow

# 3. Its outbound rules.
rule egress 100 tcp 1024-65535 0.0.0.0/0 allow
rule egress 110 tcp 443-443    0.0.0.0/0 allow

# 4. Associate it with public-a and public-b.
for s in "$PUBLIC_A" "$PUBLIC_B"; do
  ASSOC=$(aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=$s" \
    --query "NetworkAcls[0].Associations[?SubnetId=='$s'].NetworkAclAssociationId" --output text)
  aws ec2 replace-network-acl-association --association-id "$ASSOC" --network-acl-id "$ACL"
done
