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
