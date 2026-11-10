import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def appspec(acct):
    import yaml  # from the AWS tools' venv, which lab() puts on the path

    try:
        spec = yaml.safe_load(open("appspec.yml"))
    except (OSError, yaml.YAMLError) as e:
        pytest.fail(f"appspec.yml does not load as YAML: {e}")
    assert isinstance(spec, dict), "appspec.yml is empty"
    return spec


@pytest.fixture(scope="module")
def group(acct):
    cd = acct.client("codedeploy")
    try:
        return cd.get_deployment_group(applicationName="orders-api", deploymentGroupName="live")["deploymentGroupInfo"]
    except cd.exceptions.ClientError:
        pytest.fail("there is no deployment group live in the application orders-api")


def versions(acct):
    vs = acct.client("lambda").list_versions_by_function(FunctionName="orders-api")["Versions"]
    return {v["Version"]: v for v in vs}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_two_published_versions(acct):
    vs = versions(acct)
    assert "1" in vs, "version 1 of orders-api was not published"
    assert "2" in vs, "version 2 of orders-api was not published"
    assert vs["1"]["CodeSha256"] != vs["2"]["CodeSha256"], "versions 1 and 2 have the same code - publish v2.zip as version 2"


def test_alias_still_points_at_version_1(acct):
    lam = acct.client("lambda")
    try:
        a = lam.get_alias(FunctionName="orders-api", Name="live")
    except lam.exceptions.ResourceNotFoundException:
        pytest.fail("there is no alias live")
    assert a["FunctionVersion"] == "1", f"live points at {a['FunctionVersion']} - leave it on 1; shifting it is CodeDeploy's job"


def test_error_alarm_on_the_alias(acct):
    alarms = acct.client("cloudwatch").describe_alarms(AlarmNames=["orders-api-errors"])["MetricAlarms"]
    assert alarms, "there is no alarm orders-api-errors"
    a = alarms[0]
    assert (a["Namespace"], a["MetricName"]) == ("AWS/Lambda", "Errors"), "the alarm does not watch AWS/Lambda Errors"
    dims = {d["Name"]: d["Value"] for d in a.get("Dimensions", [])}
    assert dims == {"FunctionName": "orders-api", "Resource": "orders-api:live"}, f"the alarm's dimensions are {dims}, not the live alias"
    assert (a["Statistic"], a["Period"], a["EvaluationPeriods"]) == ("Sum", 60, 1), "the alarm should use Sum over 60 s for 1 period"
    assert (a["Threshold"], a["ComparisonOperator"]) == (0.0, "GreaterThanThreshold"), "the alarm should fire on any error (> 0)"
    assert a.get("TreatMissingData") == "notBreaching", "missing data should not breach - no invocations is not an error"


def test_codedeploy_role(acct):
    iam = acct.client("iam")
    try:
        trust = iam.get_role(RoleName="codedeploy-orders-api")["Role"]["AssumeRolePolicyDocument"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail("there is no role codedeploy-orders-api")
    services = [s for st in policy.statements(trust) for s in policy.as_list(st.get("Principal", {}).get("Service"))]
    assert "codedeploy.amazonaws.com" in services, "codedeploy-orders-api is not trusted by codedeploy.amazonaws.com"
    attached = [p["PolicyName"] for p in iam.list_attached_role_policies(RoleName="codedeploy-orders-api")["AttachedPolicies"]]
    assert "AWSCodeDeployRoleForLambda" in attached, "codedeploy-orders-api does not have AWSCodeDeployRoleForLambda"


def test_application_is_for_lambda(acct):
    cd = acct.client("codedeploy")
    try:
        app = cd.get_application(applicationName="orders-api")["application"]
    except cd.exceptions.ClientError:
        pytest.fail("there is no CodeDeploy application orders-api")
    assert app.get("computePlatform") == "Lambda", f"orders-api is for {app.get('computePlatform')}, not Lambda"


def test_group_is_a_canary_with_rollback(acct, group):
    assert group.get("deploymentConfigName") == "CodeDeployDefault.LambdaCanary10Percent5Minutes", f"the group uses {group.get('deploymentConfigName')}"
    style = group.get("deploymentStyle", {})
    assert (style.get("deploymentType"), style.get("deploymentOption")) == ("BLUE_GREEN", "WITH_TRAFFIC_CONTROL"), "Lambda deployments are blue/green with traffic control"
    rb = group.get("autoRollbackConfiguration", {})
    assert rb.get("enabled"), "automatic rollback is off"
    assert {"DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"} <= set(rb.get("events", [])), "roll back on both DEPLOYMENT_FAILURE and DEPLOYMENT_STOP_ON_ALARM"
    assert group.get("serviceRoleArn") == acct.client("iam").get_role(RoleName="codedeploy-orders-api")["Role"]["Arn"], "the group does not use codedeploy-orders-api"
    # The alarm configuration is not checked: the emulator accepts it but
    # does not report it back.


def test_appspec_describes_the_release(appspec):
    assert str(appspec.get("version")) == "0.0", "an AppSpec for Lambda has version 0.0"
    res = appspec.get("Resources") or []
    assert isinstance(res, list) and len(res) == 1, "Resources should be a list with one function"
    (name, body), = res[0].items()
    assert body.get("Type") == "AWS::Lambda::Function", "the resource's Type should be AWS::Lambda::Function"
    p = body.get("Properties") or {}
    assert p.get("Name") == "orders-api" and p.get("Alias") == "live", "the AppSpec should deploy orders-api on the alias live"
    assert (str(p.get("CurrentVersion")), str(p.get("TargetVersion"))) == ("1", "2"), "the AppSpec should go from version 1 to version 2"


def test_appspec_runs_the_smoke_test_first(appspec):
    hooks = {k: v for h in (appspec.get("Hooks") or []) for k, v in h.items()}
    assert hooks.get("BeforeAllowTraffic") == "orders-api-smoke", "orders-api-smoke should run as the BeforeAllowTraffic hook"
