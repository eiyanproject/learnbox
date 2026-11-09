import pytest

from awslab import lab, policy

BUCKET = "arn:aws:s3:::lb-private-data"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def endpoints(acct, service):
    eps = acct.client("ec2").describe_vpc_endpoints()["VpcEndpoints"]
    return [e for e in eps if e["ServiceName"] == f"com.amazonaws.us-east-1.{service}" and e.get("State") != "deleted"]


def private_rt(acct):
    tables = acct.by_name(acct.client("ec2").describe_route_tables()["RouteTables"])
    assert "private" in tables, "the private route table is missing - keep the part of the script that makes it"
    return tables["private"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_s3_gateway_endpoint_on_the_private_route_table(acct):
    eps = endpoints(acct, "s3")
    assert len(eps) == 1, f"there should be one S3 endpoint; there are {len(eps)}"
    ep = eps[0]
    assert ep.get("VpcEndpointType", "Gateway") == "Gateway", "the S3 endpoint should be a gateway endpoint (free, and in the route table)"
    assert private_rt(acct)["RouteTableId"] in ep.get("RouteTableIds", []), "the S3 endpoint is not on the private route table"


def test_the_endpoint_policy_allows_only_our_bucket(acct):
    doc = policy.load(endpoints(acct, "s3")[0]["PolicyDocument"])
    can = lambda action, res: policy.decide([doc], action, res).allowed  # noqa: E731
    assert can("s3:GetObject", BUCKET + "/x.csv"), "the endpoint policy does not allow GetObject on lb-private-data's objects"
    assert can("s3:PutObject", BUCKET + "/x.csv"), "the endpoint policy does not allow PutObject on lb-private-data's objects"
    assert can("s3:ListBucket", BUCKET), "the endpoint policy does not allow ListBucket on lb-private-data"
    assert not can("s3:GetObject", "arn:aws:s3:::someone-elses-bucket/x"), "the endpoint lets the VPC read any bucket in the world"
    assert not can("s3:DeleteBucket", BUCKET), "the endpoint policy allows more than get, put and list"


def test_ssm_interface_endpoint(acct):
    eps = endpoints(acct, "ssm")
    assert eps, "there is no interface endpoint for com.amazonaws.us-east-1.ssm"
    ep = eps[0]
    assert ep.get("VpcEndpointType") == "Interface", "the SSM endpoint should be an interface endpoint"
    assert ep.get("PrivateDnsEnabled"), "private DNS is off - code using ssm.us-east-1.amazonaws.com would not find the endpoint"
    subnets = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=ep["SubnetIds"])["Subnets"])
    assert set(subnets) == {"private-a", "private-b"}, f"the SSM endpoint should be in private-a and private-b; it is in {sorted(subnets)}"
    groups = [g["GroupName"] for g in ep.get("Groups", [])]
    assert groups == ["endpoints"], f"the SSM endpoint should use the endpoints security group; it uses {groups}"


def test_endpoint_security_group_allows_https_from_the_vpc(acct):
    sg = acct.client("ec2").describe_security_groups(Filters=[{"Name": "group-name", "Values": ["endpoints"]}])["SecurityGroups"]
    assert sg, "there is no security group called endpoints"
    rules = {(p.get("FromPort"), r["CidrIp"]) for p in sg[0]["IpPermissions"] for r in p.get("IpRanges", [])}
    assert rules == {(443, "10.0.0.0/16")}, f"endpoints should allow exactly TCP 443 from 10.0.0.0/16; it allows {sorted(rules, key=str)}"


def test_bucket_only_answers_through_the_endpoint(acct):
    s3 = acct.client("s3")
    try:
        doc = policy.load(s3.get_bucket_policy(Bucket="lb-private-data")["Policy"])
    except s3.exceptions.ClientError:
        pytest.fail("lb-private-data has no bucket policy")
    vpce = endpoints(acct, "s3")[0]["VpcEndpointId"]
    for st in policy.statements(doc):
        cond = (st.get("Condition") or {}).get("StringNotEquals", {})
        if st.get("Effect") == "Deny" and policy.as_list(cond.get("aws:SourceVpce")) == [vpce]:
            res = set(policy.as_list(st.get("Resource")))
            assert {BUCKET, BUCKET + "/*"} <= res, "the deny should cover the bucket and its objects"
            assert "s3:*" in policy.as_list(st.get("Action")), "the deny should cover every S3 action, s3:*"
            return
    pytest.fail(f"no Deny statement with StringNotEquals aws:SourceVpce = {vpce} (your endpoint's ID)")
