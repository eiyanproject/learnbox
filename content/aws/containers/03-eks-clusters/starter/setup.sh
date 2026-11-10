#!/usr/bin/env bash
# Containers 3: an EKS cluster.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. A KMS key, alias/eks-secrets.


# 2. Role eks-cluster (eks.amazonaws.com, AmazonEKSClusterPolicy).


# 3. Cluster platform: 1.31, private subnets, private endpoint only,
#    api/audit/authenticator logs, secrets encrypted with the key.


# 4. Role eks-node (ec2.amazonaws.com) with the three node policies.


# 5. Node group general: On-Demand m6i.large, 2-6 (2), private subnets.


# 6. Node group spot: Spot, three or more types, 0-10 (2), private subnets.


# 7. Role eks-fargate-pods and the Fargate profile batch (namespace batch).

