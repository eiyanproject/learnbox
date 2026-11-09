import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def rule(acct):
    s3 = acct.client("s3")
    try:
        rules = s3.get_bucket_lifecycle_configuration(Bucket="lb-logs")["Rules"]
    except s3.exceptions.ClientError:
        pytest.fail("lb-logs has no lifecycle configuration")
    mine = [r for r in rules if (r.get("Filter") or {}).get("Prefix", r.get("Prefix")) == "logs/"]
    assert mine, "no lifecycle rule filters on the prefix logs/"
    assert len(mine) == 1, "one rule for logs/, please - two can contradict each other"
    return mine[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_versioning_is_on(acct):
    status = acct.client("s3").get_bucket_versioning(Bucket="lb-logs").get("Status")
    assert status == "Enabled", f"versioning on lb-logs is {status or 'off'}"


def test_the_log_has_two_versions(acct):
    vs = acct.client("s3").list_object_versions(Bucket="lb-logs", Prefix="logs/app.log").get("Versions", [])
    vs = [v for v in vs if v["Key"] == "logs/app.log"]
    assert len(vs) == 2, f"logs/app.log should have 2 versions; it has {len(vs)}"
    latest = acct.client("s3").get_object(Bucket="lb-logs", Key="logs/app.log")["Body"].read().decode()
    assert "second line" in latest or len(latest.splitlines()) > 1, "the latest version should be the changed file"


def test_the_rule_is_enabled(acct):
    assert rule(acct)["Status"] == "Enabled", "the rule is not enabled"


def test_transitions(acct):
    got = sorted((t["Days"], t["StorageClass"]) for t in rule(acct).get("Transitions", []))
    assert got == [(30, "STANDARD_IA"), (90, "GLACIER")], f"transitions should be STANDARD_IA at 30 days and GLACIER at 90; got {got}"


def test_expiration(acct):
    assert rule(acct).get("Expiration", {}).get("Days") == 365, "current versions should expire after 365 days"


def test_noncurrent_versions_expire(acct):
    nve = rule(acct).get("NoncurrentVersionExpiration", {})
    assert nve.get("NoncurrentDays") == 30, "noncurrent versions should expire 30 days after they are replaced"
