import json

import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def secret(acct):
    sm = acct.client("secretsmanager")
    try:
        return sm.describe_secret(SecretId="prod/orders/db")
    except sm.exceptions.ResourceNotFoundException:
        pytest.fail("there is no secret called prod/orders/db")


def key_arn(acct):
    return acct.client("kms").describe_key(KeyId="alias/app")["KeyMetadata"]["Arn"]


def arn(acct, path):
    account = acct.client("sts").get_caller_identity()["Account"]
    return f"arn:aws:ssm:us-east-1:{account}:parameter{path}"


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_secret_uses_the_app_key_and_is_tagged(acct, secret):
    key = acct.client("kms").describe_key(KeyId=secret.get("KmsKeyId") or "alias/aws/secretsmanager")["KeyMetadata"]
    assert key["Arn"] == key_arn(acct), "the secret is not encrypted with alias/app"
    assert acct.tags(secret.get("Tags")).get("env") == "prod", "the secret is not tagged env=prod"


def test_secret_value_has_a_generated_password(acct, secret):
    raw = acct.client("secretsmanager").get_secret_value(SecretId="prod/orders/db")["SecretString"]
    try:
        value = json.loads(raw)
    except ValueError:
        pytest.fail("the secret's value is not JSON")
    assert value.get("username") == "orders", f"username is {value.get('username')!r}, not 'orders'"
    pw = str(value.get("password", ""))
    assert len(pw) == 32, f"the password is {len(pw)} characters, not 32"
    assert pw.isalnum(), "the password has punctuation - generate it with --exclude-punctuation"
    assert len(set(pw)) > 8, "that password does not look generated"


def test_rotation_every_30_days_with_rotate_db(secret):
    assert secret.get("RotationEnabled"), "rotation is not configured"
    assert secret.get("RotationLambdaARN", "").endswith(":function:rotate-db"), "rotation does not use rotate-db"
    assert secret.get("RotationRules", {}).get("AutomaticallyAfterDays") == 30, f"rotation rules are {secret.get('RotationRules')}, not every 30 days"


def test_resource_policy_lets_only_orders_app_read(acct):
    sm = acct.client("secretsmanager")
    raw = sm.get_resource_policy(SecretId="prod/orders/db").get("ResourcePolicy")
    assert raw, "the secret has no resource policy"
    doc = policy.load(raw)
    app = acct.client("iam").get_role(RoleName="orders-app")["Role"]["Arn"]
    other = app.replace("role/orders-app", "role/admin")
    d_app = policy.decide([doc], "secretsmanager:GetSecretValue", context={"aws:PrincipalArn": app})
    d_other = policy.decide([doc], "secretsmanager:GetSecretValue", context={"aws:PrincipalArn": other})
    assert d_other.result == policy.EXPLICIT_DENY, "the policy does not deny GetSecretValue to other principals"
    assert d_app.result != policy.EXPLICIT_DENY, "the policy denies orders-app too"
    principals = [st.get("Principal") for st in policy.statements(doc) if st.get("Effect") == "Deny"]
    assert "*" in principals or {"AWS": "*"} in principals, "the deny should apply to every principal (\"Principal\": \"*\")"


def test_orders_app_trusts_ecs_tasks(acct):
    trust = acct.client("iam").get_role(RoleName="orders-app")["Role"]["AssumeRolePolicyDocument"]
    services = [s for st in policy.statements(trust) for s in policy.as_list(st.get("Principal", {}).get("Service"))]
    assert "ecs-tasks.amazonaws.com" in services, "orders-app is not trusted by ecs-tasks.amazonaws.com"


@pytest.mark.parametrize("name,kind,value", [
    ("/orders/prod/db_host", "String", "orders.db.internal"),
    ("/orders/prod/allowed_origins", "StringList", "https://shop.example.com,https://admin.example.com"),
    ("/orders/prod/api_key", "SecureString", None),
])
def test_parameters(acct, name, kind, value):
    ssm = acct.client("ssm")
    try:
        p = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]
    except ssm.exceptions.ParameterNotFound:
        pytest.fail(f"there is no parameter {name}")
    assert p["Type"] == kind, f"{name} is a {p['Type']}, not a {kind}"
    if value is not None:
        assert p["Value"] == value, f"{name} is {p['Value']!r}, not {value!r}"


def test_api_key_is_encrypted_with_the_app_key(acct):
    meta = [p for p in acct.client("ssm").describe_parameters()["Parameters"] if p["Name"] == "/orders/prod/api_key"]
    assert meta, "there is no parameter /orders/prod/api_key"
    key = acct.client("kms").describe_key(KeyId=meta[0].get("KeyId", "alias/aws/ssm"))["KeyMetadata"]["Arn"]
    assert key == key_arn(acct), "/orders/prod/api_key is not encrypted with alias/app"


def test_orders_app_reads_exactly_its_config(acct, secret):
    names = acct.client("iam").list_role_policies(RoleName="orders-app")["PolicyNames"]
    assert "read-config" in names, "orders-app has no inline policy read-config"
    can = lambda action, res: acct.can("role", "orders-app", action, res)
    assert can("ssm:GetParametersByPath", arn(acct, "/orders/prod")), "orders-app cannot GetParametersByPath on /orders/prod (the path itself is the resource)"
    assert can("ssm:GetParameters", arn(acct, "/orders/prod/db_host")), "orders-app cannot GetParameters in /orders/prod"
    assert not can("ssm:GetParameters", arn(acct, "/orders/dev/db_host")), "orders-app can read /orders/dev - keep it to /orders/prod"
    assert not can("ssm:PutParameter", arn(acct, "/orders/prod/db_host")), "orders-app can write parameters"
    assert can("secretsmanager:GetSecretValue", secret["ARN"]), "orders-app cannot read the secret"
    assert not can("secretsmanager:GetSecretValue", secret["ARN"].replace("prod/orders/db", "prod/billing/db")), "orders-app can read other secrets"
    assert can("kms:Decrypt", key_arn(acct)), "orders-app cannot kms:Decrypt with the alias/app key"
    doc = policy.load(acct.client("iam").get_role_policy(RoleName="orders-app", PolicyName="read-config")["PolicyDocument"])
    wild = [w for w in policy.wildcards(doc) if w.startswith("Action")]
    assert not wild, f"read-config grants wildcard actions: {wild}"
