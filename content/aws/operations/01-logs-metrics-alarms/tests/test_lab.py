import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def topic(acct):
    arns = [t["TopicArn"] for t in acct.client("sns").list_topics()["Topics"] if t["TopicArn"].endswith(":ops-alerts")]
    assert arns, "there is no topic called ops-alerts"
    return arns[0]


def alarm(acct, name):
    found = acct.client("cloudwatch").describe_alarms(AlarmNames=[name])["MetricAlarms"]
    assert found, f"there is no alarm called {name}"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_log_group_retention(acct):
    groups = {g["logGroupName"]: g for g in acct.client("logs").describe_log_groups(logGroupNamePrefix="/app/web")["logGroups"]}
    assert "/app/web" in groups, "there is no log group /app/web"
    assert groups["/app/web"].get("retentionInDays") == 30, f"/app/web keeps logs {groups['/app/web'].get('retentionInDays') or 'forever'}, not 30 days"


def test_metric_filter(acct):
    fs = {f["filterName"]: f for f in acct.client("logs").describe_metric_filters(logGroupName="/app/web")["metricFilters"]}
    assert "errors" in fs, "there is no metric filter called errors on /app/web"
    f = fs["errors"]
    assert f["filterPattern"] == "ERROR", f"the pattern is {f['filterPattern']!r}, not ERROR"
    t = f["metricTransformations"][0]
    assert (t["metricNamespace"], t["metricName"], str(t["metricValue"])) == ("Learnbox", "AppErrors", "1"), (
        f"the filter should publish Learnbox/AppErrors with value 1; it publishes {t['metricNamespace']}/{t['metricName']} = {t['metricValue']}"
    )


def test_email_subscription(acct):
    subs = acct.client("sns").list_subscriptions_by_topic(TopicArn=topic(acct))["Subscriptions"]
    assert any(s["Protocol"] == "email" and s["Endpoint"] == "ops@example.com" for s in subs), "ops-alerts has no email subscription for ops@example.com"


def test_app_errors_alarm(acct):
    a = alarm(acct, "app-errors")
    got = (a["Namespace"], a["MetricName"], a["Statistic"], a["Period"], a["EvaluationPeriods"], a["Threshold"], a["ComparisonOperator"])
    want = ("Learnbox", "AppErrors", "Sum", 300, 1, 5.0, "GreaterThanOrEqualToThreshold")
    assert got == want, f"app-errors should be {want}; it is {got}"
    assert a.get("TreatMissingData") == "notBreaching", "missing data should count as notBreaching - errors are only published when they happen"
    assert a.get("AlarmActions") == [topic(acct)], "app-errors should notify ops-alerts"


def test_high_cpu_alarm(acct):
    a = alarm(acct, "high-cpu")
    got = (a["Namespace"], a["MetricName"], a["Statistic"], a["Period"], a["EvaluationPeriods"], a["Threshold"], a["ComparisonOperator"])
    want = ("AWS/EC2", "CPUUtilization", "Average", 300, 3, 80.0, "GreaterThanThreshold")
    assert got == want, f"high-cpu should be {want}; it is {got}"
    dims = {d["Name"]: d["Value"] for d in a.get("Dimensions", [])}
    assert dims == {"AutoScalingGroupName": "web-asg"}, f"high-cpu should watch AutoScalingGroupName=web-asg; it watches {dims or 'nothing in particular'}"
    assert a.get("AlarmActions") == [topic(acct)], "high-cpu should notify ops-alerts"
