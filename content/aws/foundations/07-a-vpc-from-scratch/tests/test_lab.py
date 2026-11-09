import pytest

from awslab import lab

SUBNETS = {
    "public-a": ("10.0.1.0/24", "us-east-1a", True),
    "public-b": ("10.0.2.0/24", "us-east-1b", True),
    "private-a": ("10.0.11.0/24", "us-east-1a", False),
    "private-b": ("10.0.12.0/24", "us-east-1b", False),
}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def vpc(acct):
    vpcs = acct.by_name(acct.client("ec2").describe_vpcs()["Vpcs"])
    assert "lb-vpc" in vpcs, "there is no VPC named lb-vpc (a Name tag)"
    return vpcs["lb-vpc"]


def subnets(acct):
    v = vpc(acct)
    found = acct.client("ec2").describe_subnets(Filters=[{"Name": "vpc-id", "Values": [v["VpcId"]]}])["Subnets"]
    return acct.by_name(found)


def route_table_for(acct, subnet_id):
    ec2 = acct.client("ec2")
    v = vpc(acct)
    tables = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [v["VpcId"]]}])["RouteTables"]
    for t in tables:
        if any(a.get("SubnetId") == subnet_id for a in t.get("Associations", [])):
            return t
    return next(t for t in tables if any(a.get("Main") for a in t.get("Associations", [])))


def has_internet_route(acct, table):
    igws = {
        g["InternetGatewayId"]
        for g in acct.client("ec2").describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc(acct)["VpcId"]]}]
        )["InternetGateways"]
    }
    return any(r.get("DestinationCidrBlock") == "0.0.0.0/0" and r.get("GatewayId") in igws for r in table["Routes"])


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_the_vpc(acct):
    assert vpc(acct)["CidrBlock"] == "10.0.0.0/16", f"lb-vpc is {vpc(acct)['CidrBlock']}, not 10.0.0.0/16"


@pytest.mark.parametrize("name", list(SUBNETS))
def test_subnet_placement(acct, name):
    cidr, az, _ = SUBNETS[name]
    s = subnets(acct)
    assert name in s, f"there is no subnet named {name} in lb-vpc"
    assert s[name]["CidrBlock"] == cidr, f"{name} is {s[name]['CidrBlock']}, not {cidr}"
    assert s[name]["AvailabilityZone"] == az, f"{name} is in {s[name]['AvailabilityZone']}, not {az}"


def test_an_internet_gateway_is_attached(acct):
    igws = acct.client("ec2").describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc(acct)["VpcId"]]}]
    )["InternetGateways"]
    assert igws, "no internet gateway is attached to lb-vpc"


@pytest.mark.parametrize("name", list(SUBNETS))
def test_routing(acct, name):
    public = SUBNETS[name][2]
    table = route_table_for(acct, subnets(acct)[name]["SubnetId"])
    if public:
        assert acct.tags(table.get("Tags")).get("Name") == "public", f"{name} should use the route table named public"
        assert has_internet_route(acct, table), f"{name}'s route table has no 0.0.0.0/0 route to the internet gateway"
    else:
        assert not has_internet_route(acct, table), f"{name} can reach the internet gateway - a private subnet must not"


@pytest.mark.parametrize("name", list(SUBNETS))
def test_public_ip_on_launch(acct, name):
    want = SUBNETS[name][2]
    got = subnets(acct)[name].get("MapPublicIpOnLaunch", False)
    assert got == want, f"{name}: public IP on launch should be {'on' if want else 'off'}"


def test_the_main_route_table_stays_private(acct):
    ec2 = acct.client("ec2")
    tables = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc(acct)["VpcId"]]}])["RouteTables"]
    main = next(t for t in tables if any(a.get("Main") for a in t.get("Associations", [])))
    assert not has_internet_route(acct, main), "the main route table routes to the internet - every unassociated subnet is now public"
