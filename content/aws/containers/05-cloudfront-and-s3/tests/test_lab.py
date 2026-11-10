import json

import pytest

from awslab import lab, policy

CACHING_OPTIMIZED = "658327ea-f89d-4fab-a63d-7e88639e58f6"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def dist(acct):
    cf = acct.client("cloudfront")
    items = cf.list_distributions().get("DistributionList", {}).get("Items", [])
    mine = [d for d in items if d.get("Comment") == "lb-site"]
    if not mine:
        pytest.fail("there is no distribution with the comment lb-site")
    d = cf.get_distribution(Id=mine[0]["Id"])["Distribution"]
    return d


@pytest.fixture(scope="module")
def oac(acct):
    items = acct.client("cloudfront").list_origin_access_controls().get("OriginAccessControlList", {}).get("Items", [])
    mine = [o for o in items if o.get("Name") == "site-oac"]
    if not mine:
        pytest.fail("there is no origin access control site-oac")
    return mine[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_bucket_is_private_and_has_the_page(acct):
    s3 = acct.client("s3")
    assert "lb-site" in acct.bucket_names(), "there is no bucket lb-site"
    try:
        pab = s3.get_public_access_block(Bucket="lb-site")["PublicAccessBlockConfiguration"]
    except s3.exceptions.ClientError:
        pytest.fail("lb-site has no Block Public Access settings")
    off = [k for k, v in pab.items() if not v]
    assert not off, f"these Block Public Access settings are off: {off}"
    try:
        head = s3.head_object(Bucket="lb-site", Key="index.html")
    except s3.exceptions.ClientError:
        pytest.fail("index.html is not in lb-site")
    assert head.get("ContentType") == "text/html", f"index.html is served as {head.get('ContentType')}, not text/html"


def test_origin_access_control(oac):
    assert (oac.get("SigningProtocol"), oac.get("SigningBehavior"), oac.get("OriginAccessControlOriginType")) == ("sigv4", "always", "s3"), "site-oac should sign every request with SigV4, for S3"


def test_origin_uses_the_oac(dist, oac):
    origins = dist["DistributionConfig"]["Origins"].get("Items", [])
    mine = [o for o in origins if o["Id"] == "s3-site"]
    assert mine, "there is no origin with the Id s3-site"
    assert mine[0]["DomainName"] == "lb-site.s3.us-east-1.amazonaws.com", f"the origin is {mine[0]['DomainName']}"
    # The emulator drops an origin's OAC, so read it from the config file.
    try:
        cfg = json.load(open("dist.json"))
    except (OSError, ValueError):
        pytest.fail("dist.json is missing or not JSON - create the distribution from it")
    assert cfg.get("Comment") == "lb-site", "dist.json is not the config of the lb-site distribution"
    file_origins = [o for o in cfg.get("Origins", {}).get("Items", []) if o.get("Id") == "s3-site"]
    assert file_origins, "dist.json has no origin s3-site"
    o = file_origins[0]
    assert o.get("OriginAccessControlId") == oac["Id"], "the origin does not use site-oac"
    assert o.get("S3OriginConfig", {}).get("OriginAccessIdentity", "") == "", "the origin still uses an origin access identity - with OAC it stays empty"


def test_distribution_settings(dist):
    cfg = dist["DistributionConfig"]
    assert cfg.get("Enabled") is True, "the distribution is disabled"
    assert cfg.get("DefaultRootObject") == "index.html", "the default root object is not index.html"
    assert cfg.get("PriceClass") == "PriceClass_100", f"the price class is {cfg.get('PriceClass')}, not PriceClass_100"


def test_default_behavior(dist):
    b = dist["DistributionConfig"]["DefaultCacheBehavior"]
    assert b.get("TargetOriginId") == "s3-site", "the default behavior does not use the s3-site origin"
    assert b.get("ViewerProtocolPolicy") == "redirect-to-https", f"viewers get {b.get('ViewerProtocolPolicy')}, not redirect-to-https"
    assert b.get("CachePolicyId") == CACHING_OPTIMIZED, "the default behavior does not use the CachingOptimized managed policy"
    assert b.get("Compress") is True, "compression is off"


def test_bucket_admits_only_this_distribution(acct, dist):
    s3 = acct.client("s3")
    try:
        doc = policy.load(s3.get_bucket_policy(Bucket="lb-site")["Policy"])
    except s3.exceptions.ClientError:
        pytest.fail("lb-site has no bucket policy")
    allows = [st for st in policy.statements(doc) if st.get("Effect") == "Allow"]
    principals = [st.get("Principal") for st in allows]
    assert all(p == {"Service": "cloudfront.amazonaws.com"} for p in principals), f"the policy allows {principals} - only the cloudfront.amazonaws.com service principal belongs here"
    obj = "arn:aws:s3:::lb-site/index.html"
    ok = policy.decide([doc], "s3:GetObject", obj, context={"AWS:SourceArn": dist["ARN"]})
    assert ok.allowed, "this distribution cannot read objects in lb-site"
    other = dist["ARN"][:-4] + "XXXX"
    assert not policy.decide([doc], "s3:GetObject", obj, context={"AWS:SourceArn": other}).allowed, "any distribution can read lb-site - add the AWS:SourceArn condition"
    assert not policy.decide([doc], "s3:PutObject", obj, context={"AWS:SourceArn": dist["ARN"]}).allowed, "CloudFront can write to the bucket"
