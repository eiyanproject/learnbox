import pytest

from awslab import lab

AL2023 = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def group(acct, name):
    ec2 = acct.client("ec2")
    vpcs = acct.by_name(ec2.describe_vpcs()["Vpcs"])
    assert "lb-vpc" in vpcs, "lb-vpc is missing - keep the part of the script that builds it"
    found = ec2.describe_security_groups(
        Filters=[{"Name": "vpc-id", "Values": [vpcs["lb-vpc"]["VpcId"]]}, {"Name": "group-name", "Values": [name]}]
    )["SecurityGroups"]
    assert found, f"there is no security group called {name} in lb-vpc"
    return found[0]


def rules(sg):
    """(port, source) for every inbound rule; the source is a CIDR or a group ID."""
    out = set()
    for p in sg["IpPermissions"]:
        port = p.get("FromPort") if p.get("FromPort") == p.get("ToPort") else (p.get("FromPort"), p.get("ToPort"))
        for r in p.get("IpRanges", []):
            out.add((port, r["CidrIp"]))
        for r in p.get("Ipv6Ranges", []):
            out.add((port, r["CidrIpv6"]))
        for g in p.get("UserIdGroupPairs", []):
            out.add((port, g["GroupId"]))
    return out


def instance(acct):
    found = [
        i
        for r in acct.client("ec2").describe_instances(Filters=[{"Name": "tag:Name", "Values": ["web"]}])["Reservations"]
        for i in r["Instances"]
        if i["State"]["Name"] != "terminated"
    ]
    assert found, "there is no instance named web"
    assert len(found) == 1, f"there are {len(found)} instances named web; launch one"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_web_allows_https_from_anywhere_and_ssh_from_the_office(acct):
    got = rules(group(acct, "web"))
    want = {(443, "0.0.0.0/0"), (22, "203.0.113.0/24")}
    assert got == want, f"web's inbound rules should be exactly {sorted(want)}; they are {sorted(got, key=str)}"


def test_ssh_is_not_open_to_the_world(acct):
    open22 = [s for p, s in rules(group(acct, "web")) if p == 22 and s in ("0.0.0.0/0", "::/0")]
    assert not open22, "port 22 is open to the whole internet"


def test_db_only_from_web(acct):
    web, db = group(acct, "web"), group(acct, "db")
    got = rules(db)
    assert got == {(5432, web["GroupId"])}, (
        f"db should allow exactly 5432 from the web group ({web['GroupId']}); it allows {sorted(got, key=str) or 'nothing'}"
    )


def test_instance_uses_the_published_al2023_ami(acct):
    want = acct.client("ssm").get_parameters(Names=[AL2023])["Parameters"][0]["Value"]
    got = instance(acct)["ImageId"]
    assert got == want, f"web runs {got}; the latest Amazon Linux 2023 AMI from Parameter Store is {want}"


def test_instance_type_and_placement(acct):
    i = instance(acct)
    assert i["InstanceType"] == "t3.micro", f"web is a {i['InstanceType']}, not a t3.micro"
    subnets = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=[i["SubnetId"]])["Subnets"])
    assert "public-a" in subnets, f"web is not in public-a (it is in {list(subnets) or i['SubnetId']})"
    sgs = [g["GroupName"] for g in i["SecurityGroups"]]
    assert sgs == ["web"], f"web should be in the web group only; it is in {sgs}"


def test_instance_has_the_role(acct):
    arn = (instance(acct).get("IamInstanceProfile") or {}).get("Arn", "")
    assert arn.endswith(":instance-profile/web-server"), f"web should have the web-server instance profile; it has {arn or 'none'}"


def test_instance_requires_imdsv2(acct):
    tokens = (instance(acct).get("MetadataOptions") or {}).get("HttpTokens")
    assert tokens == "required", f"IMDSv2 is not required (HttpTokens is {tokens or 'optional'})"
