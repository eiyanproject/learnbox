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

**Kubernetes** is the open-source standard for running containers, used
on every cloud and in data centres. It does what ECS does (keeps copies
running, rolls out versions, scales) with its own API, its own tool
`kubectl`, and a huge ecosystem of add-ons and **Helm charts** (packaged
applications). Running Kubernetes yourself is hard: its **control plane**,
the API servers and the **etcd** database holding the cluster's state, must
be highly available, backed up, patched and upgraded. **Amazon EKS**
(Elastic Kubernetes Service) runs the control plane for you, across three
Availability Zones; you decide where your containers run.

```text
 EKS cluster "platform" (control plane: run by AWS, $0.10/hour)
   API endpoint: private only ── kubectl works from inside the VPC
   logs: api, audit, authenticator ──> CloudWatch Logs
   Kubernetes Secrets ──envelope-encrypted──> KMS alias/eks-secrets
 Data plane, in private-a and private-b:
   ├── node group "general"  On-Demand m6i.large, 2-6 nodes    steady services
   ├── node group "spot"     Spot, 3 instance types, 0-10      interruptible work
   └── Fargate profile "batch"  pods in namespace batch run on Fargate, no nodes
```

## Words first, next to ECS

| Kubernetes | What it is | Closest in ECS |
|---|---|---|
| **Pod** | the smallest unit: one or more containers started together, with one IP | task |
| **Deployment** | keeps N pods of one spec running, rolls out changes | service |
| **Node** | a machine (EC2 instance) that runs pods | container instance |
| **Namespace** | a named partition of the cluster (`default`, `batch`) | cluster, loosely |
| **Control plane** | the API server and etcd that every request goes through | ECS itself |

### ECS or EKS?

| | **ECS** | **EKS** |
|---|---|---|
| API and tools | AWS's own (CLI, CloudFormation) | standard Kubernetes (`kubectl`, Helm), same as on any cloud |
| Control plane cost | free | 💸 $0.10 per hour per cluster (about $73 a month), more under extended support |
| Operating effort | low | higher: version upgrades, add-ons, Kubernetes permissions |
| Choose it when | you want the simplest way to run containers on AWS | you already use Kubernetes, need its ecosystem, or run on several clouds |

The exam rule: "Kubernetes", "existing Helm charts" or "portable across
clouds" means EKS; otherwise ECS is usually the simpler answer.

## The cluster

The **cluster role** (`eks-cluster`, trusted by `eks.amazonaws.com`, with
`AmazonEKSClusterPolicy`) lets the control plane manage AWS resources for
you, such as the network interfaces it places in your subnets so the
control plane can talk to your nodes.

- **Endpoint access.** The Kubernetes API endpoint can be **public**,
  **private**, or both. Public means reachable from the internet (still
  with authentication, and optionally limited to some CIDRs); private-only
  means `kubectl` works from inside the VPC, or over a VPN or Direct
  Connect, and from nowhere else. Private-only is the safest, and needs a
  way in for administrators and CI, such as a bastion or a runner in the VPC.
- **Control-plane logs.** Five types, all off by default: `api`, `audit`
  (who did what to the cluster), `authenticator` (which IAM identity signed
  in as which Kubernetes user), `controllerManager` and `scheduler`. They go
  to the log group `/aws/eks/CLUSTER/cluster`, 💸 billed as CloudWatch Logs.
- **Secrets encryption.** Kubernetes **Secrets** (passwords, tokens) are
  stored in etcd. With an encryption config naming your KMS key, EKS
  **envelope-encrypts** them (Security lesson 1): each Secret gets a data
  key, encrypted under your key, so the key policy and CloudTrail control
  and record their use. ❗ Once turned on it cannot be turned off, and
  deleting or disabling the key makes the cluster unable to read its
  Secrets.
- **Version.** Each Kubernetes minor version gets about **14 months** of
  standard support on EKS, then up to 12 months of **extended support**,
  at a higher hourly price; after that EKS upgrades the cluster for you.
  Upgrades go **one minor version at a time**, control plane first, then
  nodes and add-ons. (This lesson uses 1.31 because the emulator knows it;
  1.31 left standard support in late 2025, so a new real cluster should use
  a current version.)

### Who may use the cluster

Signing in with `aws eks update-kubeconfig --name platform` lets `kubectl`
authenticate with your IAM identity. What that identity may do **inside**
Kubernetes is decided by **access entries**, which map IAM principals to
Kubernetes permissions through the EKS API (the older way was the
`aws-auth` ConfigMap inside the cluster). The identity that created the
cluster gets administrator access by default.

## Where pods run

| | **Managed node group** | **Self-managed nodes** | **Fargate** |
|---|---|---|---|
| What | an Auto Scaling group EKS creates and updates | your own Auto Scaling group of EKS AMIs | one right-sized micro-VM per pod |
| Upgrades | EKS rolls new AMIs, **draining** each node (moving its pods) before replacing it | yours | none: nothing to patch |
| Limits | | | no DaemonSets, no GPUs, no privileged pods |
| Good for | most workloads | custom AMIs, unusual setups | batch jobs, small or spiky workloads |

(**Karpenter**, an open-source autoscaler, is a fourth way: it launches
right-sized instances for pending pods directly, without node groups.)

### On-Demand and Spot

**Spot** instances are spare EC2 capacity at up to 90% off, which AWS can
take back with a **two-minute** warning. A managed node group with
`capacityType SPOT` handles the warning by draining the node, so its pods
move elsewhere. Spot capacity is per instance type and AZ, so a Spot group
should name **several instance types** of the same size (`m6i.large`,
`m5.large`, `m6a.large`): when one pool runs dry, another still has
capacity. EKS picks from the pools least likely to be interrupted. Steady
services stay on On-Demand; interruptible work (batch, CI, stateless
workers) goes to Spot. A minimum of 0 lets the Spot group shrink away when
there is nothing to run.

### The node role, and pod permissions

Nodes are EC2 instances, so their role (`eks-node`) is trusted by
`ec2.amazonaws.com`, with three managed policies:

| Policy | For |
|---|---|
| `AmazonEKSWorkerNodePolicy` | the node joining the cluster |
| `AmazonEKS_CNI_Policy` | the **VPC CNI** plugin, which gives each pod its own VPC IP address (like awsvpc in ECS) |
| `AmazonEC2ContainerRegistryReadOnly` | pulling images from ECR |

❗ Every pod on a node can reach the node's role, so never give it your
applications' permissions. Pods that call AWS get their **own** role
through **EKS Pod Identity** or **IRSA** (IAM roles for service accounts),
the Kubernetes counterpart of the ECS task role.

### Fargate profiles

A **Fargate profile** has **selectors** (a namespace, optionally with
labels); pods that match run on Fargate, everything else on nodes. Its
**pod execution role**, trusted by `eks-fargate-pods.amazonaws.com` with
`AmazonEKSFargatePodExecutionRolePolicy`, pulls images and writes logs: the
counterpart of the ECS execution role. Fargate pods run in **private**
subnets only.

## Your task

Done for you: the foundations VPC (subnets `private-a` and `private-b`).

1. A KMS key with the alias **`alias/eks-secrets`**.
2. A role **`eks-cluster`** trusted by `eks.amazonaws.com` with
   `AmazonEKSClusterPolicy`.
3. A cluster **`platform`**: Kubernetes **1.31**, the role above, the two
   **private** subnets, endpoint **private only** (private access on,
   public access off), the logs `api`, `audit` and `authenticator` enabled,
   and **`secrets`** encrypted with the `alias/eks-secrets` key, given by
   its **ARN**. Wait for it with `aws eks wait cluster-active`.
4. A role **`eks-node`** trusted by `ec2.amazonaws.com` with the three node
   policies.
5. A node group **`general`**: **On-Demand**, `m6i.large` only, min **2**,
   max **6**, desired **2**, in the private subnets, with `eks-node`.
6. A node group **`spot`**: **Spot**, at least **three** instance types,
   min **0**, max **10**, desired **2**, in the private subnets, with
   `eks-node`.
7. A role **`eks-fargate-pods`** trusted by `eks-fargate-pods.amazonaws.com`
   with `AmazonEKSFargatePodExecutionRolePolicy`, and a Fargate profile
   **`batch`** using it, selecting the namespace **`batch`** only, in the
   private subnets.

A real cluster takes about ten minutes to create, and each node group a few
more; the emulator's are ready at once, but `wait cluster-active` is still
the right habit. After **Run**:

```
$ aws eks describe-cluster --name platform \
    --query 'cluster.[status,version,resourcesVpcConfig.[endpointPublicAccess,endpointPrivateAccess]]'
[
    "ACTIVE",
    "1.31",
    [
        false,
        true
    ]
]
$ aws eks describe-nodegroup --cluster-name platform --nodegroup-name spot \
    --query 'nodegroup.[capacityType,instanceTypes,scalingConfig]'
[
    "SPOT",
    [
        "m6i.large",
        "m5.large",
        "m6a.large"
    ],
    {
        "minSize": 0,
        "maxSize": 10,
        "desiredSize": 2
    }
]
```

## Check yourself

1. What does EKS manage, and what is still yours?
   *EKS runs the control plane (API servers, etcd); the nodes, add-ons,
   version upgrades and what runs in the cluster are yours (Fargate removes
   the nodes).*
2. With the endpoint private-only, why does `kubectl` from a laptop at home
   time out?
   *The API is reachable only from inside the VPC, or over VPN or Direct
   Connect.*
3. Why three instance types in the Spot group?
   *Spot capacity is per instance type and AZ; several pools mean one
   running out does not stop the group scaling.*
4. A pod needs to read an S3 bucket. Add the permission to the node role?
   *No: every pod on the node would get it. Give the pod its own role with
   Pod Identity or IRSA.*
5. Pods in the namespace `batch` run on Fargate. Where do pods in
   `default` run?
   *On the node groups: only pods matching a profile's selectors go to
   Fargate.*
