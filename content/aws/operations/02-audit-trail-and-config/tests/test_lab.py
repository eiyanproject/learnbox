import pytest

from awslab import lab, policy

BUCKET = "arn:aws:s3:::lb-audit-trail"
CLOUDTRAIL = {"Service": "cloudtrail.amazonaws.com"}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def bucket_policy(acct):
    s3 = acct.client("s3")
    try:
        return policy.statements(s3.get_bucket_policy(Bucket="lb-audit-trail")["Policy"])
    except s3.exceptions.ClientError:
        pytest.fail("lb-audit-trail has no bucket policy")


def trail(acct):
    ct = acct.client("cloudtrail")
    found = [t for t in ct.describe_trails()["trailList"] if t["Name"] == "org-trail"]
    assert found, "there is no trail called org-trail"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_cloudtrail_can_check_the_acl(acct):
    ok = [s for s in bucket_policy(acct) if s.get("Effect") == "Allow" and s.get("Principal") == CLOUDTRAIL
          and "s3:GetBucketAcl" in policy.as_list(s.get("Action")) and BUCKET in policy.as_list(s.get("Resource"))]
    assert ok, "the bucket policy should let cloudtrail.amazonaws.com s3:GetBucketAcl on arn:aws:s3:::lb-audit-trail"


def test_cloudtrail_can_write_its_logs_only(acct):
    ok = [s for s in bucket_policy(acct) if s.get("Effect") == "Allow" and s.get("Principal") == CLOUDTRAIL
          and "s3:PutObject" in policy.as_list(s.get("Action"))]
    assert ok, "the bucket policy should let cloudtrail.amazonaws.com s3:PutObject"
    s = ok[0]
    assert policy.as_list(s.get("Resource")) == [BUCKET + "/AWSLogs/123456789012/*"], "CloudTrail should only write under AWSLogs/123456789012/"
    acl = (s.get("Condition") or {}).get("StringEquals", {}).get("s3:x-amz-acl")
    assert policy.as_list(acl) == ["bucket-owner-full-control"], "the write should require the bucket-owner-full-control ACL"
    anyone = [x for x in bucket_policy(acct) if x.get("Effect") == "Allow" and x.get("Principal") in ("*", {"AWS": "*"})]
    assert not anyone, "the bucket policy allows everyone something"


def test_trail_settings(acct):
    t = trail(acct)
    assert t["S3BucketName"] == "lb-audit-trail", f"org-trail writes to {t['S3BucketName']}"
    assert t.get("IsMultiRegionTrail"), "org-trail is not multi-Region"
    assert t.get("LogFileValidationEnabled"), "log file validation is off"


def test_trail_is_logging(acct):
    assert acct.client("cloudtrail").get_trail_status(Name="org-trail")["IsLogging"], "org-trail was created but never started"


def test_config_recorder(acct):
    cfg = acct.client("config")
    recs = {r["name"]: r for r in cfg.describe_configuration_recorders()["ConfigurationRecorders"]}
    assert "default" in recs, "there is no configuration recorder called default"
    g = recs["default"].get("recordingGroup", {})
    assert g.get("allSupported") and g.get("includeGlobalResourceTypes"), "the recorder should record all supported resources, global ones included"
    status = {s["name"]: s for s in cfg.describe_configuration_recorder_status()["ConfigurationRecordersStatus"]}
    assert status.get("default", {}).get("recording"), "the recorder is not started"
    chans = cfg.describe_delivery_channels()["DeliveryChannels"]
    assert any(c.get("s3BucketName") == "lb-audit-config" for c in chans), "there is no delivery channel to lb-audit-config"


@pytest.mark.parametrize("name,ident", [("s3-versioning", "S3_BUCKET_VERSIONING_ENABLED"), ("ebs-encrypted", "ENCRYPTED_VOLUMES")])
def test_config_rule(acct, name, ident):
    rules = {r["ConfigRuleName"]: r for r in acct.client("config").describe_config_rules()["ConfigRules"]}
    assert name in rules, f"there is no Config rule called {name}"
    src = rules[name]["Source"]
    assert (src["Owner"], src["SourceIdentifier"]) == ("AWS", ident), f"{name} should be the AWS managed rule {ident}"
