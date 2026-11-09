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


def rules(sg):
    out = set()
    for p in sg["IpPermissions"]:
        for r in p.get("IpRanges", []):
            out.add((p.get("FromPort"), r["CidrIp"]))
        for g in p.get("UserIdGroupPairs", []):
            out.add((p.get("FromPort"), g["GroupId"]))
    return out


def alb(acct):
    elb = acct.client("elbv2")
    found = [l for l in elb.describe_load_balancers()["LoadBalancers"] if l["LoadBalancerName"] == "web-alb"]
    assert found, "there is no load balancer called web-alb"
    return found[0]


def target_group(acct):
    found = [t for t in acct.client("elbv2").describe_target_groups()["TargetGroups"] if t["TargetGroupName"] == "web-tg"]
    assert found, "there is no target group called web-tg"
    return found[0]


def listeners(acct):
    return {l["Port"]: l for l in acct.client("elbv2").describe_listeners(LoadBalancerArn=alb(acct)["LoadBalancerArn"])["Listeners"]}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_security_groups_chain(acct):
    a, w = group(acct, "alb"), group(acct, "web")
    assert rules(a) == {(80, "0.0.0.0/0"), (443, "0.0.0.0/0")}, f"alb should allow 80 and 443 from anywhere; it allows {sorted(rules(a), key=str)}"
    assert rules(w) == {(80, a["GroupId"])}, f"web should allow only port 80 from the alb group; it allows {sorted(rules(w), key=str)}"


def test_target_group_health_check(acct):
    t = target_group(acct)
    assert (t["Protocol"], t["Port"]) == ("HTTP", 80), f"web-tg should be HTTP on 80, not {t['Protocol']}:{t['Port']}"
    assert t.get("TargetType", "instance") == "instance", "web-tg should target instances"
    assert t.get("HealthCheckPath") == "/health", f"the health check path is {t.get('HealthCheckPath')}, not /health"
    assert (t.get("Matcher") or {}).get("HttpCode") == "200", "the health check should expect HTTP 200"


def test_load_balancer_placement(acct):
    l = alb(acct)
    assert l.get("Type", "application") == "application", "web-alb should be an Application Load Balancer"
    assert l.get("Scheme") in (None, "internet-facing"), "web-alb should be internet-facing"
    subnets = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=[z["SubnetId"] for z in l["AvailabilityZones"]])["Subnets"])
    assert set(subnets) == {"public-a", "public-b"}, f"web-alb should be in public-a and public-b; it is in {sorted(subnets)}"
    assert l.get("SecurityGroups") == [group(acct, "alb")["GroupId"]], "web-alb should use the alb security group"


def test_https_listener_forwards_with_a_certificate(acct):
    ls = listeners(acct)
    assert 443 in ls, "there is no listener on port 443"
    l = ls[443]
    assert l["Protocol"] == "HTTPS", f"the 443 listener is {l['Protocol']}, not HTTPS"
    certs = [c["CertificateArn"] for c in l.get("Certificates", [])]
    assert certs and ":acm:" in certs[0], "the HTTPS listener has no ACM certificate"
    act = l["DefaultActions"][0]
    assert act["Type"] == "forward" and act.get("TargetGroupArn") == target_group(acct)["TargetGroupArn"], "the HTTPS listener should forward to web-tg"


def test_http_redirects_to_https(acct):
    ls = listeners(acct)
    assert 80 in ls, "there is no listener on port 80"
    act = ls[80]["DefaultActions"][0]
    assert act["Type"] == "redirect", f"port 80 should redirect, not {act['Type']}"
    rc = act.get("RedirectConfig", {})
    assert (rc.get("Protocol"), str(rc.get("Port")), rc.get("StatusCode")) == ("HTTPS", "443", "HTTP_301"), (
        f"port 80 should redirect to HTTPS:443 with a 301; it redirects with {rc}"
    )
