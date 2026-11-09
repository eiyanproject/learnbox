import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def vpcs(acct):
    return acct.by_name(acct.client("ec2").describe_vpcs()["Vpcs"])


def tables(acct):
    return acct.by_name(acct.client("ec2").describe_route_tables()["RouteTables"])


def peering(acct):
    found = [
        p for p in acct.client("ec2").describe_vpc_peering_connections()["VpcPeeringConnections"]
        if p["Status"]["Code"] not in ("deleted", "rejected", "failed", "expired")
    ]
    assert found, "there is no VPC peering connection"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_peering_joins_the_two_vpcs_and_is_active(acct):
    p, v = peering(acct), vpcs(acct)
    ends = {p["RequesterVpcInfo"]["VpcId"], p["AccepterVpcInfo"]["VpcId"]}
    assert ends == {v["lb-vpc"]["VpcId"], v["data-vpc"]["VpcId"]}, "the peering connection should join lb-vpc and data-vpc"
    assert p["Status"]["Code"] == "active", f"the peering connection is {p['Status']['Code']} - it needs accepting"


@pytest.mark.parametrize("table,dest", [("private", "10.1.0.0/16"), ("data", "10.0.0.0/16")])
def test_routes_both_ways(acct, table, dest):
    t = tables(acct)
    assert table in t, f"the route table {table} is missing"
    routes = [r for r in t[table]["Routes"] if r.get("DestinationCidrBlock") == dest]
    assert routes, f"route table {table} has no route to {dest}"
    assert routes[0].get("VpcPeeringConnectionId") == peering(acct)["VpcPeeringConnectionId"], (
        f"route table {table} sends {dest} somewhere other than the peering connection"
    )


@pytest.mark.parametrize("name", ["lb-vpc", "data-vpc"])
def test_dns_hostnames_on(acct, name):
    vid = vpcs(acct)[name]["VpcId"]
    attr = acct.client("ec2").describe_vpc_attribute(VpcId=vid, Attribute="enableDnsHostnames")
    assert attr["EnableDnsHostnames"]["Value"], f"DNS hostnames are off for {name}"


def zone(acct):
    r53 = acct.client("route53")
    zones = [z for z in r53.list_hosted_zones()["HostedZones"] if z["Name"] == "internal.example."]
    assert zones, "there is no hosted zone called internal.example"
    assert zones[0]["Config"]["PrivateZone"], "internal.example is a public zone - it must be private"
    return r53.get_hosted_zone(Id=zones[0]["Id"])


def test_zone_is_associated_with_both_vpcs(acct):
    got = {v["VPCId"] for v in zone(acct).get("VPCs", [])}
    v = vpcs(acct)
    want = {v["lb-vpc"]["VpcId"], v["data-vpc"]["VpcId"]}
    assert got == want, f"internal.example should be associated with both VPCs; it has {len(got & want)} of them"


def test_db_record(acct):
    r53 = acct.client("route53")
    zid = zone(acct)["HostedZone"]["Id"]
    recs = {
        (r["Name"], r["Type"]): r
        for r in r53.list_resource_record_sets(HostedZoneId=zid)["ResourceRecordSets"]
    }
    rec = recs.get(("db.internal.example.", "A"))
    assert rec, "there is no A record for db.internal.example"
    values = [x["Value"] for x in rec.get("ResourceRecords", [])]
    assert values == ["10.1.11.10"], f"db.internal.example points at {values}, not 10.1.11.10"
