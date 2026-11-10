---
title: An EKS cluster
summary: A Kubernetes control plane with a private endpoint, control-plane logs and envelope-encrypted secrets; a managed On-Demand node group and a Spot one spread over several instance types; and a Fargate profile for batch pods.
order: 3
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "The cluster role trusts `eks.amazonaws.com` and has `arn:aws:iam::aws:policy/AmazonEKSClusterPolicy`. Node roles trust `ec2.amazonaws.com`; the Fargate pod role trusts `eks-fargate-pods.amazonaws.com`."
  - "`aws eks create-cluster --name platform --kubernetes-version 1.31 --role-arn \"$CLUSTER_ROLE\" --resources-vpc-config subnetIds=$PRIVATE_A,$PRIVATE_B,endpointPublicAccess=false,endpointPrivateAccess=true --logging '{\"clusterLogging\":[{\"types\":[\"api\",\"audit\",\"authenticator\"],\"enabled\":true}]}' --encryption-config '[{\"resources\":[\"secrets\"],\"provider\":{\"keyArn\":\"'$KEY_ARN'\"}}]'`, then `aws eks wait cluster-active --name platform`."
  - "`aws eks create-nodegroup --cluster-name platform --nodegroup-name spot --capacity-type SPOT --instance-types m6i.large m5.large m6a.large --scaling-config minSize=0,maxSize=10,desiredSize=2 --subnets $PRIVATE_A $PRIVATE_B --node-role \"$NODE_ROLE\"`."
  - "`aws eks create-fargate-profile --cluster-name platform --fargate-profile-name batch --pod-execution-role-arn \"$POD_ROLE\" --subnets $PRIVATE_A $PRIVATE_B --selectors namespace=batch`."
---

**Amazon EKS** runs the Kubernetes control plane for you - API servers and
etcd across three Availability Zones, upgraded and patched by AWS. You
choose where pods run: **managed node groups** (EC2 instances EKS creates
and updates), self-managed nodes, **Karpenter**, or **Fargate** (one
right-sized micro-VM per pod).

ECS or EKS? ECS is simpler and AWS-native. EKS is Kubernetes: the same API,
tools and Helm charts as anywhere else, at the cost of running and
upgrading a Kubernetes platform.

## The cluster

- **Endpoint access.** The API server endpoint can be public, private, or
  both. Private-only means `kubectl` works from inside the VPC (or over VPN
  or Direct Connect) and nowhere else.
- **Control-plane logs** (`api`, `audit`, `authenticator`,
  `controllerManager`, `scheduler`) go to CloudWatch Logs. `audit` records
  who did what to the cluster.
- **Secrets encryption.** Kubernetes Secrets are stored in etcd; with an
  encryption config, EKS envelope-encrypts them with your KMS key.
- **Version.** Each Kubernetes minor version is supported for a limited
  time; plan an upgrade every few months, control plane first.

## Nodes

A **managed node group** is an Auto Scaling group EKS manages: rolling
updates to new AMIs, draining nodes before replacing them. Run steady
workloads on On-Demand; run interruptible ones on a **Spot** node group
with **several instance types**, so there is always spare capacity in some
pool.

Nodes need a role with `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy`
(for the VPC CNI, which gives each pod a VPC IP) and
`AmazonEC2ContainerRegistryReadOnly`. Pods that call AWS should get their
**own** role (EKS Pod Identity or IRSA), not the node's.

## Fargate profiles

A **Fargate profile** selects pods by namespace (and labels); matching pods
run on Fargate with no nodes to manage, using a pod execution role to pull
images and write logs.

## Your task

Done for you: the foundations VPC.

1. A KMS key with the alias **`alias/eks-secrets`**.
2. A role **`eks-cluster`** trusted by `eks.amazonaws.com` with
   `AmazonEKSClusterPolicy`.
3. A cluster **`platform`**, Kubernetes **1.31**, in the two **private**
   subnets, with a **private endpoint only**, `api`, `audit` and
   `authenticator` logs on, and **secrets** encrypted with
   `alias/eks-secrets` (by its ARN).
4. A role **`eks-node`** trusted by `ec2.amazonaws.com` with the three node
   policies.
5. A node group **`general`**: On-Demand, `m6i.large`, 2 to 6 nodes (2
   desired), in the private subnets.
6. A node group **`spot`**: **Spot**, at least **three** instance types,
   0 to 10 nodes (2 desired), in the private subnets.
7. A role **`eks-fargate-pods`** trusted by
   `eks-fargate-pods.amazonaws.com` with
   `AmazonEKSFargatePodExecutionRolePolicy`, and a Fargate profile
   **`batch`** for the namespace **`batch`** in the private subnets.

(Creating a real cluster takes about ten minutes; the emulator's is ready
at once, but `aws eks wait cluster-active` is still the right habit.)
