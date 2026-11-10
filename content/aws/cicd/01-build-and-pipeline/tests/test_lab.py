import io
import json
import zipfile

import pytest

from awslab import lab, policy

BUCKET = "lb-pipeline-artifacts"
FILES = {"buildspec.yml", "app.py", "test_app.py", "template.yaml"}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def buildspec(acct):
    import yaml  # from the AWS tools' venv, which lab() puts on the path

    try:
        spec = yaml.safe_load(open("buildspec.yml"))
    except (OSError, yaml.YAMLError) as e:
        pytest.fail(f"buildspec.yml does not load as YAML: {e}")
    assert isinstance(spec, dict), "buildspec.yml is empty"
    return spec


@pytest.fixture(scope="module")
def pipeline(acct):
    cp = acct.client("codepipeline")
    try:
        return cp.get_pipeline(name="orders-api")["pipeline"]
    except cp.exceptions.PipelineNotFoundException:
        pytest.fail("there is no pipeline orders-api")


def key_arn(acct):
    return acct.client("kms").describe_key(KeyId="alias/pipeline")["KeyMetadata"]["Arn"]


def stage(pipeline, name):
    s = [x for x in pipeline.get("stages", []) if x["name"] == name]
    assert s, f"the pipeline has no stage {name}"
    assert len(s[0]["actions"]) == 1, f"the {name} stage should have one action"
    return s[0]["actions"][0]


def trusted_by(acct, role, service):
    iam = acct.client("iam")
    try:
        trust = iam.get_role(RoleName=role)["Role"]["AssumeRolePolicyDocument"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail(f"there is no role {role}")
    services = [s for st in policy.statements(trust) for s in policy.as_list(st.get("Principal", {}).get("Service"))]
    assert service in services, f"{role} is not trusted by {service}"


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_buildspec_secret_and_runtime(buildspec):
    assert str(buildspec.get("version")) == "0.2", "the buildspec version should be 0.2"
    sm = (buildspec.get("env") or {}).get("secrets-manager") or {}
    assert sm.get("SONAR_TOKEN") == "ci/sonar-token", "SONAR_TOKEN should come from secrets-manager ci/sonar-token"
    assert "SONAR_TOKEN" not in ((buildspec.get("env") or {}).get("variables") or {}), "SONAR_TOKEN is a plain variable"
    rt = ((buildspec.get("phases") or {}).get("install") or {}).get("runtime-versions") or {}
    assert str(rt.get("python")) == "3.12", "the install phase does not ask for Python 3.12"


def test_buildspec_runs_and_reports_the_tests(buildspec):
    cmds = " ".join(map(str, ((buildspec.get("phases") or {}).get("build") or {}).get("commands") or []))
    assert "pytest" in cmds and "junit" in cmds and "reports/junit.xml" in cmds, "the build phase should run pytest writing JUnit XML to reports/junit.xml"
    rep = (buildspec.get("reports") or {}).get("unit-tests") or {}
    assert rep, "there is no report group unit-tests"
    assert rep.get("file-format") == "JUNITXML", "unit-tests should be in JUNITXML format"
    found = [f"{rep.get('base-directory', '').rstrip('/')}/{f}".lstrip("/") for f in rep.get("files", [])]
    assert "reports/junit.xml" in found, "unit-tests does not pick up reports/junit.xml"


def test_buildspec_artifact_is_the_template(buildspec):
    files = ((buildspec.get("artifacts") or {}).get("files")) or []
    assert "template.yaml" in files, "template.yaml is not in the build's artifacts"


def test_bucket_is_versioned_and_encrypted_with_the_key(acct):
    s3 = acct.client("s3")
    assert BUCKET in acct.bucket_names(), f"there is no bucket {BUCKET}"
    assert s3.get_bucket_versioning(Bucket=BUCKET).get("Status") == "Enabled", "the bucket is not versioned - an S3 source action needs versioning"
    rule = s3.get_bucket_encryption(Bucket=BUCKET)["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]
    assert rule.get("SSEAlgorithm") == "aws:kms", "the bucket does not default to SSE-KMS"
    kid = rule.get("KMSMasterKeyID", "")
    assert acct.client("kms").describe_key(KeyId=kid)["KeyMetadata"]["Arn"] == key_arn(acct), "the bucket's key is not alias/pipeline"


def test_source_bundle(acct):
    s3 = acct.client("s3")
    try:
        body = s3.get_object(Bucket=BUCKET, Key="source/orders-api.zip")["Body"].read()
    except s3.exceptions.NoSuchKey:
        pytest.fail("source/orders-api.zip is not in the bucket")
    try:
        names = set(zipfile.ZipFile(io.BytesIO(body)).namelist())
    except zipfile.BadZipFile:
        pytest.fail("source/orders-api.zip is not a zip file")
    assert FILES <= names, f"the bundle is missing {sorted(FILES - names)} (at its top level)"


def test_build_role_is_least_privilege(acct):
    trusted_by(acct, "codebuild-orders-api", "codebuild.amazonaws.com")
    account = acct.client("sts").get_caller_identity()["Account"]
    secret = acct.client("secretsmanager").describe_secret(SecretId="ci/sonar-token")["ARN"]
    can = lambda a, r: acct.can("role", "codebuild-orders-api", a, r)
    assert can("logs:PutLogEvents", f"arn:aws:logs:us-east-1:{account}:log-group:/aws/codebuild/orders-api-build:log-stream:x"), "the build role cannot write its logs"
    assert can("s3:GetObject", f"arn:aws:s3:::{BUCKET}/source/orders-api.zip") and can("s3:PutObject", f"arn:aws:s3:::{BUCKET}/out.zip"), "the build role cannot read and write the artifact bucket"
    assert not can("s3:GetObject", "arn:aws:s3:::someone-elses-bucket/x"), "the build role can read other buckets"
    assert not can("s3:DeleteBucket", f"arn:aws:s3:::{BUCKET}"), "the build role can delete the bucket"
    assert can("secretsmanager:GetSecretValue", secret), "the build role cannot read ci/sonar-token"
    assert can("kms:Decrypt", key_arn(acct)) and can("kms:GenerateDataKey", key_arn(acct)), "the build role cannot use the pipeline key"


def test_codebuild_project(acct):
    projects = acct.client("codebuild").batch_get_projects(names=["orders-api-build"]).get("projects", [])
    assert projects, "there is no CodeBuild project orders-api-build"
    p = projects[0]
    assert p.get("source", {}).get("type") == "S3" and p["source"].get("location") == f"{BUCKET}/source/orders-api.zip", "the project's source is not the S3 bundle"
    env = p.get("environment", {})
    assert env.get("image") == "aws/codebuild/standard:7.0" and env.get("computeType") == "BUILD_GENERAL1_SMALL", "the project should use aws/codebuild/standard:7.0 on BUILD_GENERAL1_SMALL"
    assert p.get("timeoutInMinutes") == 20, f"the timeout is {p.get('timeoutInMinutes')} minutes, not 20"
    assert p.get("serviceRole") == acct.client("iam").get_role(RoleName="codebuild-orders-api")["Role"]["Arn"], "the project does not use codebuild-orders-api"


def test_pipeline_roles(acct, pipeline):
    trusted_by(acct, "codepipeline-orders-api", "codepipeline.amazonaws.com")
    trusted_by(acct, "cfn-deploy", "cloudformation.amazonaws.com")
    attached = [p["PolicyName"] for p in acct.client("iam").list_attached_role_policies(RoleName="cfn-deploy")["AttachedPolicies"]]
    assert "AmazonSQSFullAccess" in attached, "cfn-deploy does not have AmazonSQSFullAccess"
    assert pipeline.get("roleArn") == acct.client("iam").get_role(RoleName="codepipeline-orders-api")["Role"]["Arn"], "the pipeline does not use codepipeline-orders-api"


def test_artifact_store_is_encrypted(acct, pipeline):
    store = pipeline.get("artifactStore", {})
    assert store.get("location") == BUCKET, f"the artifact store is {store.get('location')}, not {BUCKET}"
    key = store.get("encryptionKey", {})
    assert key.get("type") == "KMS" and acct.client("kms").describe_key(KeyId=key.get("id", "x"))["KeyMetadata"]["Arn"] == key_arn(acct), "the artifact store is not encrypted with alias/pipeline"


def test_stages_in_order(pipeline):
    assert [s["name"] for s in pipeline.get("stages", [])] == ["Source", "Build", "Approve", "Deploy"], "the stages should be Source, Build, Approve, Deploy"


def test_source_and_build_actions(pipeline):
    src = stage(pipeline, "Source")
    assert src["actionTypeId"]["provider"] == "S3", "the source action is not S3"
    assert src["configuration"].get("S3Bucket") == BUCKET and src["configuration"].get("S3ObjectKey") == "source/orders-api.zip", "the source action does not read source/orders-api.zip"
    assert src["configuration"].get("PollForSourceChanges", "true").lower() == "false", "the source polls - turn PollForSourceChanges off and use the EventBridge rule"
    out = [a["name"] for a in src.get("outputArtifacts", [])]
    build = stage(pipeline, "Build")
    assert build["actionTypeId"]["provider"] == "CodeBuild" and build["configuration"].get("ProjectName") == "orders-api-build", "the build action does not run orders-api-build"
    assert [a["name"] for a in build.get("inputArtifacts", [])] == out, "the build action does not take the source's output"


def test_approval_then_deploy(acct, pipeline):
    ap = stage(pipeline, "Approve")
    assert (ap["actionTypeId"]["category"], ap["actionTypeId"]["provider"]) == ("Approval", "Manual"), "the Approve stage is not a manual approval"
    dep = stage(pipeline, "Deploy")
    assert dep["actionTypeId"]["provider"] == "CloudFormation", "the deploy action is not CloudFormation"
    c = dep["configuration"]
    assert c.get("ActionMode") == "CREATE_UPDATE" and c.get("StackName") == "orders-api", "the deploy should CREATE_UPDATE the stack orders-api"
    build_out = [a["name"] for a in stage(pipeline, "Build").get("outputArtifacts", [])]
    assert build_out and c.get("TemplatePath") == f"{build_out[0]}::template.yaml", "TemplatePath should be the build output's template.yaml"
    assert c.get("RoleArn") == acct.client("iam").get_role(RoleName="cfn-deploy")["Role"]["Arn"], "the deploy action does not hand CloudFormation the cfn-deploy role"


def test_eventbridge_starts_the_pipeline(acct):
    account = acct.client("sts").get_caller_identity()["Account"]
    pipe = f"arn:aws:codepipeline:us-east-1:{account}:orders-api"
    ev = acct.client("events")
    try:
        rule = ev.describe_rule(Name="orders-api-source")
    except ev.exceptions.ResourceNotFoundException:
        pytest.fail("there is no EventBridge rule orders-api-source")
    pat = json.loads(rule.get("EventPattern") or "{}")
    assert pat.get("source") == ["aws.s3"] and pat.get("detail-type") == ["Object Created"], "the rule should match aws.s3 Object Created events"
    detail = pat.get("detail", {})
    assert detail.get("bucket", {}).get("name") == [BUCKET] and detail.get("object", {}).get("key") == ["source/orders-api.zip"], "the rule should match the bucket and the source object's key"
    targets = ev.list_targets_by_rule(Rule="orders-api-source")["Targets"]
    role = acct.client("iam").get_role(RoleName="events-orders-api")["Role"]["Arn"]
    assert any(t["Arn"] == pipe and t.get("RoleArn") == role for t in targets), "the rule does not target the pipeline with the events-orders-api role"
    trusted_by(acct, "events-orders-api", "events.amazonaws.com")
    assert acct.can("role", "events-orders-api", "codepipeline:StartPipelineExecution", pipe), "events-orders-api cannot start the pipeline"
    assert not acct.can("role", "events-orders-api", "codepipeline:DeletePipeline", pipe), "events-orders-api can do more than start the pipeline"
    # The bucket's EventBridgeConfiguration is not checked: the emulator
    # accepts it but never reports it back.
