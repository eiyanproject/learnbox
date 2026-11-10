#!/usr/bin/env bash
# Containers 3: an EKS cluster.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

role() {  # name, service principal, managed policies...
  local name=$1 svc=$2; shift 2
  aws iam create-role --role-name "$name" \
    --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"$svc\"},\"Action\":\"sts:AssumeRole\"}]}" >/dev/null
  for p in "$@"; do
    aws iam attach-role-policy --role-name "$name" --policy-arn "arn:aws:iam::aws:policy/$p"
  done
  aws iam get-role --role-name "$name" --query Role.Arn --output text
}

# 1. A KMS key, alias/eks-secrets.
KEY_ID=$(aws kms create-key --description "EKS secrets" --query KeyMetadata.KeyId --output text)
aws kms create-alias --alias-name alias/eks-secrets --target-key-id "$KEY_ID"
KEY_ARN=$(aws kms describe-key --key-id "$KEY_ID" --query KeyMetadata.Arn --output text)

# 2. Role eks-cluster (eks.amazonaws.com, AmazonEKSClusterPolicy).
CLUSTER_ROLE=$(role eks-cluster eks.amazonaws.com AmazonEKSClusterPolicy)

# 3. Cluster platform.
aws eks create-cluster --name platform --kubernetes-version 1.31 \
  --role-arn "$CLUSTER_ROLE" \
  --resources-vpc-config "subnetIds=$PRIVATE_A,$PRIVATE_B,endpointPublicAccess=false,endpointPrivateAccess=true" \
  --logging '{"clusterLogging":[{"types":["api","audit","authenticator"],"enabled":true}]}' \
  --encryption-config "[{\"resources\":[\"secrets\"],\"provider\":{\"keyArn\":\"$KEY_ARN\"}}]" >/dev/null
aws eks wait cluster-active --name platform

# 4. Role eks-node (ec2.amazonaws.com) with the three node policies.
NODE_ROLE=$(role eks-node ec2.amazonaws.com AmazonEKSWorkerNodePolicy \
  AmazonEKS_CNI_Policy AmazonEC2ContainerRegistryReadOnly)

# 5. Node group general: On-Demand m6i.large, 2-6 (2), private subnets.
aws eks create-nodegroup --cluster-name platform --nodegroup-name general \
  --capacity-type ON_DEMAND --instance-types m6i.large \
  --scaling-config minSize=2,maxSize=6,desiredSize=2 \
  --subnets "$PRIVATE_A" "$PRIVATE_B" --node-role "$NODE_ROLE" >/dev/null

# 6. Node group spot: Spot, three or more types, 0-10 (2), private subnets.
aws eks create-nodegroup --cluster-name platform --nodegroup-name spot \
  --capacity-type SPOT --instance-types m6i.large m5.large m6a.large \
  --scaling-config minSize=0,maxSize=10,desiredSize=2 \
  --subnets "$PRIVATE_A" "$PRIVATE_B" --node-role "$NODE_ROLE" >/dev/null

# 7. Role eks-fargate-pods and the Fargate profile batch (namespace batch).
POD_ROLE=$(role eks-fargate-pods eks-fargate-pods.amazonaws.com AmazonEKSFargatePodExecutionRolePolicy)
aws eks create-fargate-profile --cluster-name platform --fargate-profile-name batch \
  --pod-execution-role-arn "$POD_ROLE" --subnets "$PRIVATE_A" "$PRIVATE_B" \
  --selectors namespace=batch >/dev/null
