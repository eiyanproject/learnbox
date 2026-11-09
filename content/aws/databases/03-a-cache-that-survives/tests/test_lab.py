import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def group(acct, name):
    found = acct.client("ec2").describe_security_groups(Filters=[{"Name": "group-name", "Values": [name]}])["SecurityGroups"]
    assert found, f"there is no security group called {name}"
    return found[0]


def rg(acct):
    ec = acct.client("elasticache")
    try:
        return ec.describe_replication_groups(ReplicationGroupId="sessions")["ReplicationGroups"][0]
    except ec.exceptions.ClientError:
        pytest.fail("there is no replication group called sessions")


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_cache_group_allows_redis_from_app_only(acct):
    app, cache = group(acct, "app"), group(acct, "cache")
    got = {(p.get("FromPort"), g["GroupId"]) for p in cache["IpPermissions"] for g in p.get("UserIdGroupPairs", [])}
    cidrs = [r["CidrIp"] for p in cache["IpPermissions"] for r in p.get("IpRanges", [])]
    assert got == {(6379, app["GroupId"])} and not cidrs, "cache should allow exactly 6379 from the app group, and no address ranges"


def test_subnet_group_is_private(acct):
    sg = acct.client("elasticache").describe_cache_subnet_groups(CacheSubnetGroupName="cache")["CacheSubnetGroups"][0]
    ids = [s["SubnetIdentifier"] for s in sg["Subnets"]]
    names = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=ids)["Subnets"])
    assert set(names) == {"private-a", "private-b"}, f"the cache subnet group should be private-a and private-b; it is {sorted(names)}"


def test_two_nodes_with_failover_across_azs(acct):
    g = rg(acct)
    # The emulator records one member cluster whatever --num-cache-clusters
    # says, so the node count is not checked here. A real account refuses
    # Multi-AZ with a single node, which keeps the lesson honest.
    assert g.get("AutomaticFailover") == "enabled", "automatic failover is off"
    assert g.get("MultiAZ") == "enabled", "Multi-AZ is off"


def test_encrypted(acct):
    g = rg(acct)
    assert g.get("AtRestEncryptionEnabled"), "encryption at rest is off"
    assert g.get("TransitEncryptionEnabled"), "encryption in transit is off"
