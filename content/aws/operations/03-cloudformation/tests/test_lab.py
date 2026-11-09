import json

import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def stack(acct):
    cf = acct.client("cloudformation")
    try:
        return cf.describe_stacks(StackName="app-dev")["Stacks"][0]
    except cf.exceptions.ClientError:
        pytest.fail("there is no stack called app-dev")


def resources(acct):
    rs = acct.client("cloudformation").describe_stack_resources(StackName="app-dev")["StackResources"]
    return {r["LogicalResourceId"]: r for r in rs}


def outputs(acct):
    return {o["OutputKey"]: o["OutputValue"] for o in stack(acct).get("Outputs", [])}


def queue_attrs(acct, logical):
    url = resources(acct)[logical]["PhysicalResourceId"]
    sqs = acct.client("sqs")
    if not url.startswith("http"):
        url = sqs.get_queue_url(QueueName=url.rsplit("/", 1)[-1])["QueueUrl"]
    name = url.rsplit("/", 1)[-1]
    url = sqs.get_queue_url(QueueName=name)["QueueUrl"]
    return sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])["Attributes"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_stack_is_complete_with_its_parameter_and_tag(acct):
    s = stack(acct)
    assert s["StackStatus"] == "CREATE_COMPLETE", f"app-dev is {s['StackStatus']}"
    params = {p["ParameterKey"]: p["ParameterValue"] for p in s.get("Parameters", [])}
    assert params.get("Env") == "dev", f"Env should be dev; parameters are {params}"
    tags = {t["Key"]: t["Value"] for t in s.get("Tags", [])}
    assert tags.get("env") == "dev", "the stack should be tagged env=dev"
    assert s.get("EnableTerminationProtection"), "termination protection is off"


def test_the_template_restricts_env(acct):
    body = acct.client("cloudformation").get_template(StackName="app-dev")["TemplateBody"]
    text = body if isinstance(body, str) else json.dumps(body)
    assert "AllowedValues" in text, "the Env parameter should have AllowedValues dev and prod"


def test_resources(acct):
    r = resources(acct)
    want = {"Uploads": "AWS::S3::Bucket", "DeadLetters": "AWS::SQS::Queue", "Jobs": "AWS::SQS::Queue"}
    got = {k: v["ResourceType"] for k, v in r.items()}
    assert got == want, f"the stack should hold {want}; it holds {got}"


def test_uploads_bucket(acct):
    name = resources(acct)["Uploads"]["PhysicalResourceId"]
    s3 = acct.client("s3")
    assert s3.get_bucket_versioning(Bucket=name).get("Status") == "Enabled", "Uploads has versioning off"
    algo = s3.get_bucket_encryption(Bucket=name)["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
    assert algo == "aws:kms", f"Uploads is encrypted with {algo}, not aws:kms"
    pab = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
    assert all(pab.get(k) for k in ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"]), "Uploads should block public access, all four settings"
    tags = {t["Key"]: t["Value"] for t in s3.get_bucket_tagging(Bucket=name)["TagSet"]}
    assert tags.get("env") == "dev", "Uploads should be tagged env with the parameter's value"


def test_queues(acct):
    assert queue_attrs(acct, "DeadLetters").get("MessageRetentionPeriod") == "1209600", "DeadLetters should keep messages 14 days"
    jobs = queue_attrs(acct, "Jobs")
    assert jobs.get("VisibilityTimeout") == "120", f"Jobs has a visibility timeout of {jobs.get('VisibilityTimeout')}"
    rp = json.loads(jobs.get("RedrivePolicy", "{}"))
    assert rp.get("deadLetterTargetArn") == queue_attrs(acct, "DeadLetters")["QueueArn"], "Jobs should redrive to DeadLetters"
    assert str(rp.get("maxReceiveCount")) == "5", "Jobs should redrive after 5 receives"


def test_outputs(acct):
    o = outputs(acct)
    assert o.get("UploadsBucket") == resources(acct)["Uploads"]["PhysicalResourceId"], "the UploadsBucket output should be !Ref Uploads"
    assert "JobsQueueUrl" in o, "there is no JobsQueueUrl output"
