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


def template_resource(acct, logical):
    """A resource's Properties as the deployed template declares them."""
    import yaml

    class Loader(yaml.SafeLoader):
        pass

    # CloudFormation's short forms (!Ref, !GetAtt, !Sub...) become plain
    # {"Ref": ...}-style values, enough to check what was declared.
    def tag(loader, suffix, node):
        key = "Ref" if suffix == "Ref" else "Fn::" + suffix
        if isinstance(node, yaml.ScalarNode):
            return {key: loader.construct_scalar(node)}
        if isinstance(node, yaml.SequenceNode):
            return {key: loader.construct_sequence(node)}
        return {key: loader.construct_mapping(node)}

    Loader.add_multi_constructor("!", tag)
    body = acct.client("cloudformation").get_template(StackName="app-dev")["TemplateBody"]
    doc = body if isinstance(body, dict) else yaml.load(body, Loader=Loader)
    return (doc.get("Resources", {}).get(logical) or {}).get("Properties", {})


def test_uploads_bucket_is_encrypted(acct):
    name = resources(acct)["Uploads"]["PhysicalResourceId"]
    rules = acct.client("s3").get_bucket_encryption(Bucket=name)["ServerSideEncryptionConfiguration"]["Rules"]
    algo = rules[0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
    assert algo == "aws:kms", f"Uploads is encrypted with {algo}, not aws:kms"


# The emulator's CloudFormation creates the bucket and applies its encryption
# but not every other property, so these are checked as the template
# declares them - which is what a real stack would build.
def test_uploads_bucket_declares_versioning_blocking_and_tag(acct):
    props = template_resource(acct, "Uploads")
    assert (props.get("VersioningConfiguration") or {}).get("Status") == "Enabled", "Uploads should declare VersioningConfiguration Status: Enabled"
    pab = props.get("PublicAccessBlockConfiguration") or {}
    missing = [k for k in ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"] if pab.get(k) is not True]
    assert not missing, f"Uploads should block public access; not set to true: {', '.join(missing)}"
    tags = {t.get("Key"): t.get("Value") for t in props.get("Tags", [])}
    assert tags.get("env") == {"Ref": "Env"}, "Uploads should be tagged env with !Ref Env"


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
