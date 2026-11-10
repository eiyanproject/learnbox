import json

import pytest

from awslab import lab

INSTANCE = "arn:aws:ec2:us-east-1:111122223333:instance/*"
SUBNET = "arn:aws:ec2:us-east-1:111122223333:subnet/subnet-0abc"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def org(acct):
    o = acct.client("organizations")
    try:
        o.describe_organization()
    except o.exceptions.AWSOrganizationsNotInUseException:
        pytest.fail("there is no organization")
    return o


def ou_id(org, name, parent=None):
    parent = parent or org.list_roots()["Roots"][0]["Id"]
    for ou in org.list_organizational_units_for_parent(ParentId=parent)["OrganizationalUnits"]:
        if ou["Name"] == name:
            return ou["Id"]
    pytest.fail(f"there is no OU {name} under {'the root' if parent.startswith('r-') else parent}")


def account_id(org, name):
    for a in org.list_accounts()["Accounts"]:
        if a["Name"] == name:
            return a["Id"]
    pytest.fail(f"there is no account called {name}")


def attached(org, target, kind="SERVICE_CONTROL_POLICY"):
    return {p["Name"] for p in org.list_policies_for_target(TargetId=target, Filter=kind)["Policies"]}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_all_features_and_policy_types(org):
    assert org.describe_organization()["Organization"]["FeatureSet"] == "ALL", "the organization does not have all features"
    types = {t["Type"]: t["Status"] for t in org.list_roots()["Roots"][0].get("PolicyTypes", [])}
    for t in ("SERVICE_CONTROL_POLICY", "TAG_POLICY"):
        assert types.get(t) == "ENABLED", f"{t} is not enabled on the root"


def test_ou_tree(org):
    workloads = ou_id(org, "Workloads")
    ou_id(org, "Security")
    ou_id(org, "Prod", workloads)
    ou_id(org, "Dev", workloads)


@pytest.mark.parametrize("name,ou,under", [("log-archive", "Security", None), ("app-prod", "Prod", "Workloads"), ("app-dev", "Dev", "Workloads")])
def test_accounts_are_in_their_ous(org, name, ou, under):
    parent = ou_id(org, ou, ou_id(org, under) if under else None)
    got = org.list_parents(ChildId=account_id(org, name))["Parents"][0]["Id"]
    assert got == parent, f"{name} is not in the {ou} OU"


def test_policies_are_attached_where_asked(org):
    root = org.list_roots()["Roots"][0]["Id"]
    workloads = ou_id(org, "Workloads")
    assert "baseline-guardrails" in attached(org, root), "baseline-guardrails is not attached to the root"
    assert "region-guard" in attached(org, workloads), "region-guard is not attached to Workloads"
    assert "dev-instance-types" in attached(org, ou_id(org, "Dev", workloads)), "dev-instance-types is not attached to Dev"
    assert "cost-center" in attached(org, root, "TAG_POLICY"), "the tag policy cost-center is not attached to the root"
    assert "FullAWSAccess" in attached(org, root), "FullAWSAccess was removed from the root - with deny-list SCPs it must stay, or nothing is allowed"


@pytest.mark.parametrize("name", ["log-archive", "app-prod", "app-dev"])
@pytest.mark.parametrize("action", ["organizations:LeaveOrganization", "cloudtrail:StopLogging", "cloudtrail:DeleteTrail", "guardduty:DeleteDetector"])
def test_baseline_guardrails_apply_everywhere(acct, org, name, action):
    assert not acct.scp_allows(account_id(org, name), action, context={"aws:RequestedRegion": "us-east-1"}), f"{name} can still {action}"


def test_ordinary_work_is_still_allowed(acct, org):
    for name in ("log-archive", "app-prod", "app-dev"):
        assert acct.scp_allows(account_id(org, name), "s3:PutObject", context={"aws:RequestedRegion": "us-east-1"}), f"the SCPs block s3:PutObject in {name} - deny lists should block only what they name"


def test_workloads_are_kept_to_two_regions(acct, org):
    prod = account_id(org, "app-prod")
    ctx = lambda r: {"aws:RequestedRegion": r, "ec2:InstanceType": "t3.micro"}
    assert not acct.scp_allows(prod, "ec2:RunInstances", INSTANCE, ctx("ap-south-1")), "app-prod can launch instances in ap-south-1"
    assert acct.scp_allows(prod, "ec2:RunInstances", INSTANCE, ctx("eu-west-1")), "app-prod cannot launch instances in eu-west-1"
    for action in ("iam:CreateRole", "sts:AssumeRole", "route53:ChangeResourceRecordSets", "cloudfront:CreateInvalidation"):
        assert acct.scp_allows(prod, action, context={"aws:RequestedRegion": "us-east-1" if action.startswith("iam") else "ap-south-1"}), f"region-guard blocks the global action {action} - exclude it with NotAction"
    log = account_id(org, "log-archive")
    assert acct.scp_allows(log, "s3:PutObject", context={"aws:RequestedRegion": "ap-south-1"}), "the Region guard reaches the Security OU - attach it to Workloads only"


def test_dev_is_limited_to_burstable_instances(acct, org):
    dev, prod = account_id(org, "app-dev"), account_id(org, "app-prod")
    ctx = lambda t: {"aws:RequestedRegion": "us-east-1", "ec2:InstanceType": t}
    assert not acct.scp_allows(dev, "ec2:RunInstances", INSTANCE, ctx("m5.large")), "app-dev can launch an m5.large"
    assert acct.scp_allows(dev, "ec2:RunInstances", INSTANCE, ctx("t3.micro")), "app-dev cannot launch a t3.micro"
    assert acct.scp_allows(dev, "ec2:RunInstances", INSTANCE, ctx("t4g.small")), "app-dev cannot launch a t4g.small"
    assert acct.scp_allows(prod, "ec2:RunInstances", INSTANCE, ctx("m5.large")), "the instance-type limit reaches app-prod - attach it to Dev only"
    no_type = {"aws:RequestedRegion": "us-east-1"}
    assert acct.scp_allows(dev, "ec2:RunInstances", SUBNET, no_type), (
        "dev-instance-types also denies RunInstances on the subnet, which has no instance type - "
        "so no instance can ever launch. Scope its Resource to arn:aws:ec2:*:*:instance/*")


def test_tag_policy_defines_cost_center(org):
    pols = org.list_policies(Filter="TAG_POLICY")["Policies"]
    mine = [p for p in pols if p["Name"] == "cost-center"]
    assert mine, "there is no tag policy called cost-center"
    content = json.loads(org.describe_policy(PolicyId=mine[0]["Id"])["Policy"]["Content"])
    assert "CostCenter" in content.get("tags", {}), "the tag policy does not define the key CostCenter"
