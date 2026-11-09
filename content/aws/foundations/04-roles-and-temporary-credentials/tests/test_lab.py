import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def role(acct, name):
    iam = acct.client("iam")
    try:
        return iam.get_role(RoleName=name)["Role"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail(f"there is no role called {name}")


def trust(acct, name):
    return policy.statements(role(acct, name)["AssumeRolePolicyDocument"])


def attached(acct, name):
    iam = acct.client("iam")
    return [p["PolicyArn"] for p in iam.list_attached_role_policies(RoleName=name)["AttachedPolicies"]]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_web_server_trusts_ec2_and_nothing_else(acct):
    sts = trust(acct, "web-server")
    allows = [s for s in sts if s.get("Effect") == "Allow" and "sts:AssumeRole" in policy.as_list(s.get("Action"))]
    assert allows, "web-server's trust policy allows nobody to sts:AssumeRole"
    principals = [s.get("Principal") for s in allows]
    assert principals == [{"Service": "ec2.amazonaws.com"}], (
        f"web-server should trust only the EC2 service, Principal {{\"Service\": \"ec2.amazonaws.com\"}}; it trusts {principals}"
    )


def test_web_server_can_read_s3(acct):
    assert "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" in attached(acct, "web-server"), (
        "web-server should have AmazonS3ReadOnlyAccess attached"
    )


def test_web_server_has_an_instance_profile(acct):
    iam = acct.client("iam")
    try:
        ip = iam.get_instance_profile(InstanceProfileName="web-server")["InstanceProfile"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail("there is no instance profile called web-server")
    roles = [r["RoleName"] for r in ip["Roles"]]
    assert roles == ["web-server"], f"the instance profile should hold the web-server role; it holds {roles or 'nothing'}"


def test_auditor_trusts_the_other_account(acct):
    allows = [s for s in trust(acct, "auditor") if s.get("Effect") == "Allow"]
    principals = [policy.as_list((s.get("Principal") or {}).get("AWS")) for s in allows]
    flat = [p for ps in principals for p in ps]
    assert flat and all(p in ("arn:aws:iam::111122223333:root", "111122223333") for p in flat), (
        f"auditor should trust account 111122223333 (arn:aws:iam::111122223333:root); it trusts {flat or 'nobody'}"
    )


def test_auditor_needs_the_external_id(acct):
    for s in trust(acct, "auditor"):
        if s.get("Effect") != "Allow":
            continue
        cond = (s.get("Condition") or {}).get("StringEquals", {})
        assert policy.as_list(cond.get("sts:ExternalId")) == ["lb-audit-2026"], (
            "every Allow in auditor's trust policy needs Condition StringEquals sts:ExternalId = lb-audit-2026"
        )


def test_auditor_has_security_audit(acct):
    assert attached(acct, "auditor") == ["arn:aws:iam::aws:policy/SecurityAudit"], (
        f"auditor should have exactly SecurityAudit attached; it has {attached(acct, 'auditor') or 'nothing'}"
    )
