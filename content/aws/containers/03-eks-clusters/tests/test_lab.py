import pytest

from awslab import lab, policy

NODE_POLICIES = {"AmazonEKSWorkerNodePolicy", "AmazonEKS_CNI_Policy", "AmazonEC2ContainerRegistryReadOnly"}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def cluster(acct):
    eks = acct.client("eks")
    try:
        return eks.describe_cluster(name="platform")["cluster"]
    except eks.exceptions.ResourceNotFoundException:
        pytest.fail("there is no cluster called platform")


def private(acct):
    by = acct.by_name(acct.client("ec2").describe_subnets()["Subnets"])
    return {by["private-a"]["SubnetId"], by["private-b"]["SubnetId"]}


def nodegroup(acct, name):
    eks = acct.client("eks")
    try:
        return eks.describe_nodegroup(clusterName="platform", nodegroupName=name)["nodegroup"]
    except eks.exceptions.ResourceNotFoundException:
        pytest.fail(f"there is no node group {name}")


def role(acct, name, service, managed):
    iam = acct.client("iam")
    try:
        r = iam.get_role(RoleName=name)["Role"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail(f"there is no role {name}")
    services = [s for st in policy.statements(r["AssumeRolePolicyDocument"]) for s in policy.as_list(st.get("Principal", {}).get("Service"))]
    assert service in services, f"{name} is not trusted by {service}"
    attached = {p["PolicyName"] for p in iam.list_attached_role_policies(RoleName=name)["AttachedPolicies"]}
    missing = set(managed) - attached
    assert not missing, f"{name} is missing {sorted(missing)}"
    return r["Arn"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_cluster_role(acct, cluster):
    assert cluster.get("roleArn") == role(acct, "eks-cluster", "eks.amazonaws.com", {"AmazonEKSClusterPolicy"}), "the cluster does not use eks-cluster"


def test_cluster_version_and_subnets(acct, cluster):
    assert cluster.get("version") == "1.31", f"the cluster runs Kubernetes {cluster.get('version')}, not 1.31"
    assert set(cluster.get("resourcesVpcConfig", {}).get("subnetIds", [])) == private(acct), "the cluster is not in the two private subnets"


def test_endpoint_is_private_only(cluster):
    vpc = cluster.get("resourcesVpcConfig", {})
    assert vpc.get("endpointPrivateAccess") is True, "the private endpoint is off"
    assert vpc.get("endpointPublicAccess") is False, "the API server is reachable from the internet"


def test_control_plane_logs(cluster):
    on = {t for entry in cluster.get("logging", {}).get("clusterLogging", []) if entry.get("enabled") for t in entry.get("types", [])}
    missing = {"api", "audit", "authenticator"} - on
    assert not missing, f"these control-plane logs are off: {sorted(missing)}"


def test_secrets_are_envelope_encrypted(acct, cluster):
    key = acct.client("kms").describe_key(KeyId="alias/eks-secrets")["KeyMetadata"]["Arn"]
    enc = cluster.get("encryptionConfig", [])
    assert any("secrets" in e.get("resources", []) and e.get("provider", {}).get("keyArn") == key for e in enc), "Kubernetes secrets are not encrypted with the alias/eks-secrets key"


def test_node_role(acct):
    role(acct, "eks-node", "ec2.amazonaws.com", NODE_POLICIES)


def test_general_node_group(acct):
    ng = nodegroup(acct, "general")
    assert ng.get("capacityType") == "ON_DEMAND", "general is not On-Demand"
    assert ng.get("instanceTypes") == ["m6i.large"], f"general uses {ng.get('instanceTypes')}, not m6i.large"
    sc = ng.get("scalingConfig", {})
    assert (sc.get("minSize"), sc.get("maxSize"), sc.get("desiredSize")) == (2, 6, 2), f"general scales {sc}, not 2-6 with 2 desired"
    assert set(ng.get("subnets", [])) == private(acct), "general is not in the private subnets"
    assert ng.get("nodeRole") == acct.client("iam").get_role(RoleName="eks-node")["Role"]["Arn"], "general does not use eks-node"


def test_spot_node_group_is_diversified(acct):
    ng = nodegroup(acct, "spot")
    assert ng.get("capacityType") == "SPOT", "spot is not a Spot node group"
    assert len(set(ng.get("instanceTypes", []))) >= 3, "spot should use at least three instance types, so capacity is always available somewhere"
    sc = ng.get("scalingConfig", {})
    assert (sc.get("minSize"), sc.get("maxSize"), sc.get("desiredSize")) == (0, 10, 2), f"spot scales {sc}, not 0-10 with 2 desired"
    assert set(ng.get("subnets", [])) == private(acct), "spot is not in the private subnets"


def test_fargate_profile_for_batch(acct):
    arn = role(acct, "eks-fargate-pods", "eks-fargate-pods.amazonaws.com", {"AmazonEKSFargatePodExecutionRolePolicy"})
    eks = acct.client("eks")
    try:
        fp = eks.describe_fargate_profile(clusterName="platform", fargateProfileName="batch")["fargateProfile"]
    except eks.exceptions.ResourceNotFoundException:
        pytest.fail("there is no Fargate profile batch")
    assert fp.get("podExecutionRoleArn") == arn, "the profile does not use eks-fargate-pods"
    assert [s.get("namespace") for s in fp.get("selectors", [])] == ["batch"], "the profile should select the namespace batch"
    assert set(fp.get("subnets", [])) == private(acct), "the profile is not in the private subnets"
