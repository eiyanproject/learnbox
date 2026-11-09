import pytest

from awslab import lab

READ_ONLY = "arn:aws:iam::aws:policy/ReadOnlyAccess"


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_developers_has_read_only_access(acct):
    iam = acct.client("iam")
    groups = [g["GroupName"] for g in iam.list_groups()["Groups"]]
    assert "developers" in groups, "there is no group called developers"
    attached = [p["PolicyArn"] for p in iam.list_attached_group_policies(GroupName="developers")["AttachedPolicies"]]
    assert READ_ONLY in attached, f"developers should have {READ_ONLY} attached; it has {attached or 'nothing'}"


@pytest.mark.parametrize("user", ["alice", "bob"])
def test_user_is_in_developers(acct, user):
    iam = acct.client("iam")
    users = [u["UserName"] for u in iam.list_users()["Users"]]
    assert user in users, f"there is no user called {user}"
    groups = [g["GroupName"] for g in iam.list_groups_for_user(UserName=user)["Groups"]]
    assert "developers" in groups, f"{user} is not in developers"


@pytest.mark.parametrize("user", ["alice", "bob"])
def test_user_has_no_policies_of_their_own(acct, user):
    iam = acct.client("iam")
    attached = iam.list_attached_user_policies(UserName=user)["AttachedPolicies"]
    inline = iam.list_user_policies(UserName=user)["PolicyNames"]
    assert not attached and not inline, (
        f"{user} has policies of their own ({[p['PolicyName'] for p in attached] + inline}); "
        "permissions belong on the group"
    )


def test_users_can_read_but_not_write(acct):
    # Through the group alone: ReadOnlyAccess allows Describe/Get/List, never Put.
    assert acct.can("user", "alice", "ec2:DescribeInstances"), "alice cannot even describe instances"
    assert not acct.can("user", "alice", "s3:PutObject", "arn:aws:s3:::any-bucket/key"), "alice can write to S3"


def test_password_policy(acct):
    iam = acct.client("iam")
    try:
        pp = iam.get_account_password_policy()["PasswordPolicy"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail("there is no account password policy")
    assert pp.get("MinimumPasswordLength", 0) >= 14, f"minimum length is {pp.get('MinimumPasswordLength')}, not 14 or more"
    for key in ["RequireSymbols", "RequireNumbers", "RequireUppercaseCharacters", "RequireLowercaseCharacters"]:
        assert pp.get(key), f"the password policy does not set {key}"
