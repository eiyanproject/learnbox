import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def account(acct):
    return acct.client("sts").get_caller_identity()["Account"]


@pytest.fixture(scope="module")
def taskdef(acct):
    ecs = acct.client("ecs")
    try:
        return ecs.describe_task_definition(taskDefinition="orders-api")["taskDefinition"]
    except ecs.exceptions.ClientError:
        pytest.fail("there is no task definition orders-api")


@pytest.fixture(scope="module")
def service(acct):
    svcs = acct.client("ecs").describe_services(cluster="apps", services=["orders-api"]).get("services", [])
    if not svcs:
        pytest.fail("there is no service orders-api in the cluster apps")
    return svcs[0]


def container(taskdef):
    cs = [c for c in taskdef.get("containerDefinitions", []) if c.get("name") == "orders-api"]
    assert cs, "the task definition has no container called orders-api"
    return cs[0]


def subnet_ids(acct, *names):
    by = acct.by_name(acct.client("ec2").describe_subnets()["Subnets"])
    return {by[n]["SubnetId"] for n in names}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_log_group_keeps_30_days(acct):
    groups = acct.client("logs").describe_log_groups(logGroupNamePrefix="/ecs/orders-api")["logGroups"]
    g = [x for x in groups if x["logGroupName"] == "/ecs/orders-api"]
    assert g, "there is no log group /ecs/orders-api"
    assert g[0].get("retentionInDays") == 30, f"/ecs/orders-api keeps logs for {g[0].get('retentionInDays', 'ever')} days, not 30"


@pytest.mark.parametrize("name", ["orders-api-execution", "orders-api-task"])
def test_roles_trust_ecs_tasks(acct, name):
    iam = acct.client("iam")
    try:
        trust = iam.get_role(RoleName=name)["Role"]["AssumeRolePolicyDocument"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail(f"there is no role {name}")
    services = [s for st in policy.statements(trust) for s in policy.as_list(st.get("Principal", {}).get("Service"))]
    assert "ecs-tasks.amazonaws.com" in services, f"{name} is not trusted by ecs-tasks.amazonaws.com"


def test_execution_role_has_the_managed_policy(acct):
    attached = [p["PolicyName"] for p in acct.client("iam").list_attached_role_policies(RoleName="orders-api-execution")["AttachedPolicies"]]
    assert "AmazonECSTaskExecutionRolePolicy" in attached, "orders-api-execution does not have AmazonECSTaskExecutionRolePolicy"


def test_task_role_reaches_only_the_orders_table(acct, account):
    table = f"arn:aws:dynamodb:us-east-1:{account}:table/orders"
    for action in ("dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query"):
        assert acct.can("role", "orders-api-task", action, table), f"orders-api-task cannot {action} on orders"
    assert not acct.can("role", "orders-api-task", "dynamodb:DeleteTable", table), "orders-api-task can delete the table"
    assert not acct.can("role", "orders-api-task", "dynamodb:GetItem", table.replace("orders", "billing")), "orders-api-task can read other tables"
    assert not acct.can("role", "orders-api-task", "ecr:BatchGetImage", "*"), "the task role can pull images - that is the execution role's job"


def test_cluster_has_container_insights(acct):
    cl = acct.client("ecs").describe_clusters(clusters=["apps"], include=["SETTINGS"]).get("clusters", [])
    assert cl and cl[0].get("status") == "ACTIVE", "there is no cluster apps"
    settings = {s["name"]: s["value"] for s in cl[0].get("settings", [])}
    assert settings.get("containerInsights") == "enabled", "Container Insights is not enabled on apps"


def test_task_definition_is_for_fargate(taskdef):
    assert "FARGATE" in taskdef.get("requiresCompatibilities", []), "the task definition is not for FARGATE"
    assert taskdef.get("networkMode") == "awsvpc", "Fargate tasks need networkMode awsvpc"
    assert (taskdef.get("cpu"), taskdef.get("memory")) == ("512", "1024"), f"the task has {taskdef.get('cpu')} CPU / {taskdef.get('memory')} MiB, not 512 / 1024"


def test_task_definition_roles(acct, taskdef):
    iam = acct.client("iam")
    assert taskdef.get("executionRoleArn") == iam.get_role(RoleName="orders-api-execution")["Role"]["Arn"], "the execution role is not orders-api-execution"
    assert taskdef.get("taskRoleArn") == iam.get_role(RoleName="orders-api-task")["Role"]["Arn"], "the task role is not orders-api-task"


def test_container(acct, taskdef, account):
    c = container(taskdef)
    assert c.get("image") == f"{account}.dkr.ecr.us-east-1.amazonaws.com/orders-api:release-1", f"the image is {c.get('image')}"
    assert any(p.get("containerPort") == 8080 for p in c.get("portMappings", [])), "the container does not map port 8080"
    log = c.get("logConfiguration", {})
    assert log.get("logDriver") == "awslogs" and log.get("options", {}).get("awslogs-group") == "/ecs/orders-api", "the container does not log to /ecs/orders-api with awslogs"
    secret = acct.client("secretsmanager").describe_secret(SecretId="prod/orders/db")["ARN"]
    secrets = {s["name"]: s["valueFrom"] for s in c.get("secrets", [])}
    assert secrets.get("DB_PASSWORD") == secret, "DB_PASSWORD is not injected from the prod/orders/db secret (use secrets, not environment)"
    assert not any(e.get("name") == "DB_PASSWORD" for e in c.get("environment", [])), "DB_PASSWORD is a plain environment variable"


def test_security_group_allows_8080_from_the_vpc_only(acct):
    sgs = [g for g in acct.client("ec2").describe_security_groups()["SecurityGroups"] if g["GroupName"] == "orders-api"]
    assert sgs, "there is no security group orders-api"
    rules = sgs[0]["IpPermissions"]
    assert any(r.get("FromPort") == 8080 and r.get("ToPort") == 8080 and {"CidrIp": "10.0.0.0/16"} in [{"CidrIp": x["CidrIp"]} for x in r.get("IpRanges", [])] for r in rules), "orders-api does not allow 8080 from 10.0.0.0/16"
    cidrs = {x["CidrIp"] for r in rules for x in r.get("IpRanges", [])}
    assert "0.0.0.0/0" not in cidrs, "orders-api is open to the internet"


def test_service_runs_two_private_tasks(acct, service):
    assert service.get("desiredCount") == 2, f"the service wants {service.get('desiredCount')} tasks, not 2"
    assert service.get("launchType") == "FARGATE", "the service does not use Fargate"
    net = service.get("networkConfiguration", {}).get("awsvpcConfiguration", {})
    assert set(net.get("subnets", [])) == subnet_ids(acct, "private-a", "private-b"), "the service is not in the two private subnets"
    assert net.get("assignPublicIp") == "DISABLED", "the tasks get public IPs"
    sg = [g["GroupId"] for g in acct.client("ec2").describe_security_groups()["SecurityGroups"] if g["GroupName"] == "orders-api"]
    assert sg and net.get("securityGroups") == sg, "the service does not use the orders-api security group"


def test_deployments_roll_back_by_themselves(service):
    dc = service.get("deploymentConfiguration", {})
    cb = dc.get("deploymentCircuitBreaker", {})
    assert cb.get("enable") and cb.get("rollback"), "the deployment circuit breaker is not on with rollback"
    assert (dc.get("minimumHealthyPercent"), dc.get("maximumPercent")) == (100, 200), f"min/max healthy is {dc.get('minimumHealthyPercent')}/{dc.get('maximumPercent')}, not 100/200"


def test_auto_scaling_on_cpu(acct):
    aas = acct.client("application-autoscaling")
    targets = aas.describe_scalable_targets(ServiceNamespace="ecs", ResourceIds=["service/apps/orders-api"])["ScalableTargets"]
    assert targets, "the service is not registered with Application Auto Scaling"
    assert (targets[0]["MinCapacity"], targets[0]["MaxCapacity"]) == (2, 10), f"scaling is {targets[0]['MinCapacity']}-{targets[0]['MaxCapacity']}, not 2-10"
    pols = aas.describe_scaling_policies(ServiceNamespace="ecs", ResourceId="service/apps/orders-api")["ScalingPolicies"]
    tt = [p for p in pols if p["PolicyType"] == "TargetTrackingScaling"]
    assert tt, "there is no target tracking policy"
    cfg = tt[0]["TargetTrackingScalingPolicyConfiguration"]
    assert cfg.get("PredefinedMetricSpecification", {}).get("PredefinedMetricType") == "ECSServiceAverageCPUUtilization", "the policy does not track average CPU"
    assert float(cfg.get("TargetValue")) == 60.0, f"the target is {cfg.get('TargetValue')}, not 60"
