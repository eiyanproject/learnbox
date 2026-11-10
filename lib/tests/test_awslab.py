"""awslab's pure parts: the policy evaluator and the endpoint guard.

These need neither the emulator nor boto3, so they run anywhere:

    PYTHONPATH=lib python -m pytest lib/tests/test_awslab.py
"""

from awslab import policy
from awslab.__main__ import with_endpoint

READ_REPORTS = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": "s3:ListBucket", "Resource": "arn:aws:s3:::lb-reports"},
        {"Effect": "Allow", "Action": "s3:Get*", "Resource": "arn:aws:s3:::lb-reports/*"},
        {"Effect": "Deny", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::lb-reports/private/*"},
    ],
}


def decide(action, resource, docs=(READ_REPORTS,)):
    return policy.decide(docs, action, resource).result


def test_allow_matches_action_wildcards_case_insensitively():
    assert decide("s3:GetObject", "arn:aws:s3:::lb-reports/a.csv") == policy.ALLOW
    assert decide("S3:getobject", "arn:aws:s3:::lb-reports/a.csv") == policy.ALLOW


def test_resources_match_case_sensitively():
    assert decide("s3:GetObject", "arn:aws:s3:::LB-REPORTS/a.csv") == policy.IMPLICIT_DENY


def test_explicit_deny_beats_allow():
    assert decide("s3:GetObject", "arn:aws:s3:::lb-reports/private/pay.csv") == policy.EXPLICIT_DENY


def test_nothing_allowed_is_an_implicit_deny():
    assert decide("s3:PutObject", "arn:aws:s3:::lb-reports/a.csv") == policy.IMPLICIT_DENY


def test_bucket_and_objects_are_different_resources():
    assert decide("s3:ListBucket", "arn:aws:s3:::lb-reports") == policy.ALLOW
    assert decide("s3:ListBucket", "arn:aws:s3:::lb-reports/x") == policy.IMPLICIT_DENY


def test_not_action_and_not_resource():
    doc = {"Statement": [{"Effect": "Allow", "NotAction": "iam:*", "NotResource": "arn:aws:s3:::secret/*"}]}
    assert decide("s3:GetObject", "arn:aws:s3:::open/x", [doc]) == policy.ALLOW
    assert decide("iam:CreateUser", "*", [doc]) == policy.IMPLICIT_DENY
    assert decide("s3:GetObject", "arn:aws:s3:::secret/x", [doc]) == policy.IMPLICIT_DENY


def test_conditional_statements_are_reported_not_guessed():
    doc = {"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*", "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}}]}
    d = policy.decide([doc], "s3:GetObject", "arn:aws:s3:::x/y")
    assert d.result == policy.IMPLICIT_DENY and len(d.conditional) == 1


def test_wildcards_finds_broad_grants_only_in_allows():
    assert policy.wildcards({"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}]}) == ["Action s3:*", "Resource *"]
    assert policy.wildcards({"Statement": [{"Effect": "Deny", "Action": "*", "Resource": "*"}]}) == []
    assert policy.wildcards(READ_REPORTS) == []


def test_load_accepts_url_encoded_documents():
    # IAM returns policy documents URL-encoded on some calls.
    assert policy.load("%7B%22Statement%22%3A%20%5B%5D%7D") == {"Statement": []}


def test_every_cli_call_gets_the_sandbox_endpoint():
    # CLI v1 ignores AWS_ENDPOINT_URL for SQS and RDS; the option must be there.
    assert with_endpoint(["sqs", "list-queues"], "http://127.0.0.1:4599") == [
        "--endpoint-url", "http://127.0.0.1:4599", "sqs", "list-queues",
    ]


def test_a_learners_own_endpoint_is_kept():
    args = ["s3", "ls", "--endpoint-url", "http://127.0.0.1:9000"]
    assert with_endpoint(args, "http://127.0.0.1:4599") == args
    args = ["s3", "ls", "--endpoint-url=http://127.0.0.1:9000"]
    assert with_endpoint(args, "http://127.0.0.1:4599") == args


REGION_GUARD = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "DenyOutsideApprovedRegions",
        "Effect": "Deny",
        "NotAction": ["iam:*", "organizations:*", "sts:*", "support:*"],
        "Resource": "*",
        "Condition": {"StringNotEquals": {"aws:RequestedRegion": ["us-east-1", "eu-west-1"]}},
    }],
}
FULL = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}


def test_conditions_are_set_aside_without_a_context():
    d = policy.decide([REGION_GUARD, FULL], "ec2:RunInstances")
    assert d.result == policy.ALLOW and len(d.conditional) == 1


def test_negated_condition_denies_outside_the_list():
    assert policy.decide([REGION_GUARD, FULL], "ec2:RunInstances", context={"aws:RequestedRegion": "ap-south-1"}).result == policy.EXPLICIT_DENY
    assert policy.decide([REGION_GUARD, FULL], "ec2:RunInstances", context={"aws:requestedregion": "eu-west-1"}).result == policy.ALLOW


def test_missing_key_makes_negated_operators_true_and_others_false():
    only_tls = {"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*", "Condition": {"Bool": {"aws:SecureTransport": "true"}}}]}
    assert policy.decide([only_tls], "s3:GetObject", context={}).result == policy.IMPLICIT_DENY
    assert policy.decide([REGION_GUARD, FULL], "ec2:RunInstances", context={}).result == policy.EXPLICIT_DENY
    if_exists = {"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*", "Condition": {"StringEqualsIfExists": {"s3:prefix": "home/"}}}]}
    assert policy.decide([if_exists], "s3:ListBucket", context={}).result == policy.ALLOW


def test_like_null_and_unmodelled_operators():
    arn_like = {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*", "Condition": {"ArnLike": {"aws:PrincipalArn": "arn:aws:iam::*:role/admin-*"}}}]}
    assert policy.decide([arn_like], "s3:GetObject", context={"aws:PrincipalArn": "arn:aws:iam::111122223333:role/admin-ops"}).allowed
    assert not policy.decide([arn_like], "s3:GetObject", context={"aws:PrincipalArn": "arn:aws:iam::111122223333:role/dev"}).allowed
    tag_required = {"Statement": [{"Effect": "Deny", "Action": "ec2:RunInstances", "Resource": "*", "Condition": {"Null": {"aws:RequestTag/CostCenter": "true"}}}]}
    assert policy.decide([tag_required, FULL], "ec2:RunInstances", context={}).result == policy.EXPLICIT_DENY
    assert policy.decide([tag_required, FULL], "ec2:RunInstances", context={"aws:RequestTag/CostCenter": "42"}).result == policy.ALLOW
    numeric = {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*", "Condition": {"NumericLessThan": {"x": "1"}}}]}
    try:
        policy.decide([numeric], "s3:GetObject", context={"x": "0"})
    except ValueError:
        pass
    else:
        raise AssertionError("an unmodelled operator should raise")


def test_scps_need_an_allow_at_every_level_and_deny_wins():
    leave = {"Statement": [{"Effect": "Deny", "Action": "organizations:LeaveOrganization", "Resource": "*"}]}
    only_s3 = {"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}]}
    assert policy.scp_decide([[FULL], [FULL, leave]], "ec2:RunInstances").allowed
    assert policy.scp_decide([[FULL], [FULL, leave]], "organizations:LeaveOrganization").result == policy.EXPLICIT_DENY
    # An OU that replaced FullAWSAccess with an allow list blocks everything else.
    assert policy.scp_decide([[FULL], [only_s3]], "ec2:RunInstances").result == policy.IMPLICIT_DENY
    assert policy.scp_decide([[FULL], [only_s3]], "s3:GetObject").allowed
    assert policy.scp_decide([[FULL, REGION_GUARD]], "ec2:RunInstances", context={"aws:RequestedRegion": "ap-south-1"}).result == policy.EXPLICIT_DENY
    assert policy.scp_decide([[FULL, REGION_GUARD]], "iam:CreateRole", context={"aws:RequestedRegion": "ap-south-1"}).allowed
