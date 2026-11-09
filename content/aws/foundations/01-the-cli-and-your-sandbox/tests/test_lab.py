import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_lb_first_bucket_exists_in_us_east_1(acct):
    assert "lb-first-bucket" in acct.bucket_names(), "there is no bucket called lb-first-bucket"
    where = acct.client("s3").get_bucket_location(Bucket="lb-first-bucket")["LocationConstraint"]
    # S3 reports us-east-1 as no constraint at all: a quirk older than Regions.
    assert where in (None, "us-east-1"), f"lb-first-bucket is in {where}, not us-east-1"


def test_lb_first_bucket_is_tagged(acct):
    s3 = acct.client("s3")
    try:
        tags = acct.tags(s3.get_bucket_tagging(Bucket="lb-first-bucket")["TagSet"])
    except s3.exceptions.ClientError:
        tags = {}
    assert tags.get("project") == "learnbox", f"lb-first-bucket should have the tag project=learnbox; it has {tags or 'none'}"


def test_lb_tokyo_bucket_is_in_tokyo(acct):
    assert "lb-tokyo-bucket" in acct.bucket_names(), "there is no bucket called lb-tokyo-bucket"
    where = acct.client("s3").get_bucket_location(Bucket="lb-tokyo-bucket")["LocationConstraint"]
    assert where == "ap-northeast-1", f"lb-tokyo-bucket is in {where or 'us-east-1'}, not ap-northeast-1"
