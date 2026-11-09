import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def key_for_alias(acct):
    kms = acct.client("kms")
    aliases = {a["AliasName"]: a.get("TargetKeyId") for a in kms.list_aliases()["Aliases"]}
    assert "alias/lb-data" in aliases, "there is no KMS alias called alias/lb-data"
    return aliases["alias/lb-data"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_block_public_access(acct):
    s3 = acct.client("s3")
    try:
        cfg = s3.get_public_access_block(Bucket="lb-data")["PublicAccessBlockConfiguration"]
    except s3.exceptions.ClientError:
        pytest.fail("lb-data has no Block Public Access configuration")
    off = [k for k in ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"] if not cfg.get(k)]
    assert not off, f"Block Public Access settings still off: {', '.join(off)}"


def test_the_key_rotates(acct):
    key = key_for_alias(acct)
    assert acct.client("kms").get_key_rotation_status(KeyId=key)["KeyRotationEnabled"], "rotation is off for alias/lb-data's key"


def test_default_encryption_is_sse_kms_with_that_key(acct):
    rules = acct.client("s3").get_bucket_encryption(Bucket="lb-data")["ServerSideEncryptionConfiguration"]["Rules"]
    by_default = rules[0]["ApplyServerSideEncryptionByDefault"]
    assert by_default["SSEAlgorithm"] == "aws:kms", f"default encryption is {by_default['SSEAlgorithm']}, not aws:kms"
    named = by_default.get("KMSMasterKeyID", "")
    key = key_for_alias(acct)
    assert named in ("alias/lb-data", key) or named.endswith(key) or named.endswith("alias/lb-data"), (
        f"default encryption uses {named or 'the AWS managed key'}, not alias/lb-data"
    )
    assert rules[0].get("BucketKeyEnabled"), "the S3 Bucket Key is not enabled"


def test_the_report_is_there(acct):
    keys = [o["Key"] for o in acct.client("s3").list_objects_v2(Bucket="lb-data").get("Contents", [])]
    assert "report.csv" in keys, "report.csv is not in lb-data"


def test_insecure_transport_is_denied(acct):
    s3 = acct.client("s3")
    try:
        doc = policy.load(s3.get_bucket_policy(Bucket="lb-data")["Policy"])
    except s3.exceptions.ClientError:
        pytest.fail("lb-data has no bucket policy")
    good = False
    for st in policy.statements(doc):
        cond = (st.get("Condition") or {}).get("Bool", {})
        if (
            st.get("Effect") == "Deny"
            and st.get("Principal") in ("*", {"AWS": "*"})
            and str(cond.get("aws:SecureTransport")).lower() == "false"
        ):
            res = set(policy.as_list(st.get("Resource")))
            acts = policy.as_list(st.get("Action"))
            assert {"arn:aws:s3:::lb-data", "arn:aws:s3:::lb-data/*"} <= res, (
                "the TLS statement must cover the bucket and its objects: arn:aws:s3:::lb-data and arn:aws:s3:::lb-data/*"
            )
            assert "s3:*" in acts, "the TLS statement should deny every S3 action, s3:*"
            good = True
    assert good, "no statement denies requests with aws:SecureTransport false to everyone (Principal \"*\")"


def test_the_policy_bites(acct):
    # The sandbox is plain HTTP: with the policy on, an upload must now fail.
    s3 = acct.client("s3")
    with pytest.raises(s3.exceptions.ClientError):
        s3.put_object(Bucket="lb-data", Key="over-http.csv", Body=b"x")
