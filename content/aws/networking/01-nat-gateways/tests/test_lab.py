import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def subnets(acct):
    return acct.by_name(acct.client("ec2").describe_subnets()["Subnets"])


def nat_gateways(acct):
    return [n for n in acct.client("ec2").describe_nat_gateways()["NatGateways"] if n["State"] not in ("deleted", "deleting", "failed")]


def table_for(acct, subnet_id):
    for t in acct.client("ec2").describe_route_tables()["RouteTables"]:
        if any(a.get("SubnetId") == subnet_id for a in t.get("Associations", [])):
            return t
    return None


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_one_nat_gateway_in_each_public_subnet(acct):
    s = subnets(acct)
    where = sorted(n["SubnetId"] for n in nat_gateways(acct))
    want = sorted([s["public-a"]["SubnetId"], s["public-b"]["SubnetId"]])
    assert where == want, (
        f"there should be one NAT gateway in public-a and one in public-b; found {len(where)} "
        f"in {[k for k, v in s.items() if v['SubnetId'] in where]}"
    )


def test_each_nat_gateway_has_an_elastic_ip(acct):
    for n in nat_gateways(acct):
        assert any(a.get("AllocationId") for a in n["NatGatewayAddresses"]), f"{n['NatGatewayId']} has no Elastic IP"


@pytest.mark.parametrize("az", ["a", "b"])
def test_private_subnet_goes_out_through_its_own_az(acct, az):
    s = subnets(acct)
    t = table_for(acct, s[f"private-{az}"]["SubnetId"])
    assert t is not None, f"private-{az} has no route table of its own (it is using the main one)"
    assert acct.tags(t.get("Tags")).get("Name") == f"private-{az}", f"private-{az}'s route table should be named private-{az}"
    default = [r for r in t["Routes"] if r.get("DestinationCidrBlock") == "0.0.0.0/0"]
    assert default and default[0].get("NatGatewayId"), f"private-{az}'s route table has no 0.0.0.0/0 route to a NAT gateway"
    nat = {n["NatGatewayId"]: n for n in nat_gateways(acct)}[default[0]["NatGatewayId"]]
    assert nat["SubnetId"] == s[f"public-{az}"]["SubnetId"], (
        f"private-{az} uses the NAT gateway in another AZ - if that AZ fails, so does private-{az}'s internet"
    )


@pytest.mark.parametrize("az", ["a", "b"])
def test_private_subnets_have_no_internet_gateway_route(acct, az):
    t = table_for(acct, subnets(acct)[f"private-{az}"]["SubnetId"])
    if t:
        igw = [r for r in t["Routes"] if str(r.get("GatewayId", "")).startswith("igw-")]
        assert not igw, f"private-{az} routes to the internet gateway - that makes it public"
