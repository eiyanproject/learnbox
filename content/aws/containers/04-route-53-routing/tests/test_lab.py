import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def zone(acct, name, private):
    zones = acct.client("route53").list_hosted_zones()["HostedZones"]
    mine = [z for z in zones if z["Name"] == name + "." and z.get("Config", {}).get("PrivateZone", False) == private]
    if not mine:
        pytest.fail(f"there is no {'private' if private else 'public'} hosted zone {name}")
    return mine[0]


def records(acct, zone_id, name, kind="A"):
    sets = acct.client("route53").list_resource_record_sets(HostedZoneId=zone_id)["ResourceRecordSets"]
    return [r for r in sets if r["Name"] == name + "." and r["Type"] == kind]


def values(r):
    return [x["Value"] for x in r.get("ResourceRecords", [])]


@pytest.fixture(scope="module")
def public(acct):
    return zone(acct, "example.com", False)["Id"]


@pytest.fixture(scope="module")
def health_check(acct):
    checks = acct.client("route53").list_health_checks()["HealthChecks"]
    mine = [c for c in checks if c["HealthCheckConfig"].get("IPAddress") == "192.0.2.10"]
    if not mine:
        pytest.fail("there is no health check on 192.0.2.10")
    return mine[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_health_check(health_check):
    c = health_check["HealthCheckConfig"]
    assert c.get("Type") == "HTTPS" and c.get("Port") == 443, f"the check is {c.get('Type')} on port {c.get('Port')}, not HTTPS 443"
    assert c.get("ResourcePath") == "/health", f"the check requests {c.get('ResourcePath')}, not /health"
    assert c.get("RequestInterval") == 30 and c.get("FailureThreshold") == 3, "the check should run every 30 s and fail after 3 failures"


def test_failover_pair(acct, public, health_check):
    rs = {r.get("Failover"): r for r in records(acct, public, "app.example.com")}
    assert "PRIMARY" in rs and "SECONDARY" in rs, "app.example.com needs a PRIMARY and a SECONDARY failover record"
    assert values(rs["PRIMARY"]) == ["192.0.2.10"], "the primary should answer 192.0.2.10"
    assert values(rs["SECONDARY"]) == ["198.51.100.10"], "the secondary should answer 198.51.100.10"
    assert rs["PRIMARY"].get("HealthCheckId") == health_check["Id"], "the primary is not tied to the health check - without it, Route 53 never fails over"
    for r in rs.values():
        assert r.get("TTL") == 60, f"{r.get('SetIdentifier')} has TTL {r.get('TTL')}, not 60"


def test_weighted_canary(acct, public):
    rs = {r.get("SetIdentifier"): r for r in records(acct, public, "www.example.com")}
    assert set(rs) == {"blue", "green"}, f"www.example.com has the sets {sorted(k for k in rs if k)}, not blue and green"
    assert (rs["blue"].get("Weight"), values(rs["blue"])) == (90, ["192.0.2.20"]), "blue should send weight 90 to 192.0.2.20"
    assert (rs["green"].get("Weight"), values(rs["green"])) == (10, ["192.0.2.30"]), "green should send weight 10 to 192.0.2.30"


def test_latency_records(acct, public):
    rs = {r.get("Region"): r for r in records(acct, public, "api.example.com")}
    assert set(rs) == {"us-east-1", "eu-west-1"}, "api.example.com needs latency records for us-east-1 and eu-west-1"
    assert values(rs["us-east-1"]) == ["192.0.2.40"] and values(rs["eu-west-1"]) == ["198.51.100.40"], "the latency records point at the wrong addresses"


def test_private_zone_for_the_vpc(acct):
    z = zone(acct, "internal.example.com", True)
    vpc = acct.by_name(acct.client("ec2").describe_vpcs()["Vpcs"])["lb-vpc"]["VpcId"]
    vpcs = [v["VPCId"] for v in acct.client("route53").get_hosted_zone(Id=z["Id"]).get("VPCs", [])]
    assert vpc in vpcs, "internal.example.com is not associated with the VPC"
    attr = acct.client("ec2").describe_vpc_attribute(VpcId=vpc, Attribute="enableDnsHostnames")["EnableDnsHostnames"]["Value"]
    assert attr, "enableDnsHostnames is off in the VPC"
    rs = records(acct, z["Id"], "db.internal.example.com", "CNAME")
    assert rs, "there is no CNAME db.internal.example.com in the private zone"
    assert values(rs[0]) == ["orders.cluster-abc.us-east-1.rds.amazonaws.com"], "db.internal.example.com points somewhere else"
    assert rs[0].get("TTL") == 300, f"db.internal.example.com has TTL {rs[0].get('TTL')}, not 300"


def test_internal_name_is_not_public(acct, public):
    assert not records(acct, public, "db.internal.example.com", "CNAME"), "db.internal.example.com is in the public zone - it belongs in the private one"
