import pytest

from awslab import lab, policy

BUCKET = "arn:aws:s3:::lb-reports"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def reports_read(acct):
    iam = acct.client("iam")
    pols = {p["PolicyName"]: p for p in iam.list_policies(Scope="Local")["Policies"]}
    assert "reports-read" in pols, "there is no customer managed policy called reports-read"
    p = pols["reports-read"]
    return policy.load(iam.get_policy_version(PolicyArn=p["Arn"], VersionId=p["DefaultVersionId"])["PolicyVersion"]["Document"])


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_reports_read_is_attached_to_analysts_and_carol_is_in_it(acct):
    iam = acct.client("iam")
    attached = [p["PolicyName"] for p in iam.list_attached_group_policies(GroupName="analysts")["AttachedPolicies"]]
    assert "reports-read" in attached, f"analysts should have reports-read attached; it has {attached or 'nothing'}"
    groups = [g["GroupName"] for g in iam.list_groups_for_user(UserName="carol")["Groups"]]
    assert groups == ["analysts"], f"carol should be in analysts only; she is in {groups or 'no group'}"


def test_carol_can_list_the_bucket(acct):
    assert acct.can("user", "carol", "s3:ListBucket", BUCKET), (
        "carol cannot list lb-reports. s3:ListBucket acts on the bucket itself: arn:aws:s3:::lb-reports, no /*"
    )


def test_carol_can_read_a_report(acct):
    assert acct.can("user", "carol", "s3:GetObject", BUCKET + "/q1.csv"), (
        "carol cannot read q1.csv. s3:GetObject acts on objects: arn:aws:s3:::lb-reports/*"
    )


def test_carol_cannot_read_private_files(acct):
    d = policy.decide(acct.policy_documents("user", "carol"), "s3:GetObject", BUCKET + "/private/salaries.csv")
    assert d.result == policy.EXPLICIT_DENY, (
        "private/salaries.csv should be explicitly denied - a Deny statement on arn:aws:s3:::lb-reports/private/*"
        if d.result == policy.ALLOW
        else "private/ is denied, but only because nothing allows it; the lesson asks for an explicit Deny"
    )


@pytest.mark.parametrize("action", ["s3:PutObject", "s3:DeleteObject"])
def test_carol_cannot_change_anything(acct, action):
    assert not acct.can("user", "carol", action, BUCKET + "/q1.csv"), f"carol is allowed {action}"


def test_no_wildcard_grants(acct):
    found = policy.wildcards(reports_read(acct))
    assert not found, f"reports-read allows {', '.join(found)} - least privilege means naming the actions and resources"
