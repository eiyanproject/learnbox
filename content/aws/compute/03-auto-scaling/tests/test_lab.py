import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def group(acct):
    found = acct.client("autoscaling").describe_auto_scaling_groups(AutoScalingGroupNames=["web-asg"])["AutoScalingGroups"]
    assert found, "there is no Auto Scaling group called web-asg"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_template_and_sizes(acct):
    g = group(acct)
    lt = g.get("LaunchTemplate") or {}
    assert lt.get("LaunchTemplateName") == "web", "web-asg should launch from the template web"
    assert lt.get("Version") == "$Default", f"web-asg should follow the template's $Default version, not {lt.get('Version')}"
    sizes = (g["MinSize"], g["MaxSize"], g["DesiredCapacity"])
    assert sizes == (2, 6, 2), f"min, max and desired should be 2, 6 and 2; they are {sizes}"


def test_spread_over_the_private_subnets(acct):
    ids = [s for s in group(acct)["VPCZoneIdentifier"].split(",") if s]
    names = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=ids)["Subnets"])
    assert set(names) == {"private-a", "private-b"}, f"web-asg should use private-a and private-b; it uses {sorted(names)}"


def test_behind_the_target_group_with_elb_health_checks(acct):
    g = group(acct)
    tg = acct.client("elbv2").describe_target_groups(Names=["web-tg"])["TargetGroups"][0]["TargetGroupArn"]
    assert g.get("TargetGroupARNs") == [tg], "web-asg should register its instances with web-tg"
    assert g["HealthCheckType"] == "ELB", "web-asg should use ELB health checks, so an instance failing /health is replaced"
    assert g["HealthCheckGracePeriod"] == 300, f"the grace period is {g['HealthCheckGracePeriod']}s, not 300"


def test_target_tracking_on_cpu(acct):
    pols = acct.client("autoscaling").describe_policies(AutoScalingGroupName="web-asg")["ScalingPolicies"]
    tt = [p for p in pols if p["PolicyType"] == "TargetTrackingScaling"]
    assert tt, "web-asg has no target tracking policy"
    cfg = tt[0]["TargetTrackingConfiguration"]
    metric = (cfg.get("PredefinedMetricSpecification") or {}).get("PredefinedMetricType")
    assert metric == "ASGAverageCPUUtilization", f"the policy tracks {metric}, not average CPU"
    assert cfg["TargetValue"] == 50, f"the target is {cfg['TargetValue']}, not 50"


@pytest.mark.parametrize("name,cron,size", [("weekday-morning", "45 7 * * 1-5", 4), ("weekday-evening", "0 19 * * 1-5", 2)])
def test_scheduled_actions(acct, name, cron, size):
    acts = {a["ScheduledActionName"]: a for a in acct.client("autoscaling").describe_scheduled_actions(AutoScalingGroupName="web-asg")["ScheduledUpdateGroupActions"]}
    assert name in acts, f"there is no scheduled action called {name}"
    a = acts[name]
    assert a.get("Recurrence") == cron, f"{name} runs at '{a.get('Recurrence')}', not '{cron}'"
    assert a.get("DesiredCapacity") == size and a.get("MinSize") == size, f"{name} should set min and desired to {size}"
