import importlib.util
import json

import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def fn(acct):
    lam = acct.client("lambda")
    try:
        return lam.get_function(FunctionName="process-order")
    except lam.exceptions.ResourceNotFoundException:
        pytest.fail("there is no function called process-order")


def handler():
    spec = importlib.util.spec_from_file_location("lesson_handler", "handler.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.handler


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_handler_reports_only_the_bad_messages():
    event = {"Records": [
        {"messageId": "m1", "body": json.dumps({"order": 1})},
        {"messageId": "m2", "body": "not json at all"},
        {"messageId": "m3", "body": json.dumps({"customer": 9})},
        {"messageId": "m4", "body": json.dumps({"order": 4, "total": 10})},
    ]}
    got = handler()(event, None)
    ids = sorted(f["itemIdentifier"] for f in got.get("batchItemFailures", []))
    assert ids == ["m2", "m3"], f"for a batch where m2 is not JSON and m3 has no order, the handler reported {ids}"


def test_handler_with_a_good_batch_reports_nothing():
    got = handler()({"Records": [{"messageId": "a", "body": '{"order": 1}'}]}, None)
    assert got == {"batchItemFailures": []}, f"a batch with nothing wrong should return no failures, not {got}"


def test_execution_role(acct):
    iam = acct.client("iam")
    role = iam.get_role(RoleName="process-order")["Role"]
    trust = policy.statements(role["AssumeRolePolicyDocument"])
    assert any(s.get("Principal") == {"Service": "lambda.amazonaws.com"} for s in trust), "process-order's role should trust lambda.amazonaws.com"
    attached = [p["PolicyArn"] for p in iam.list_attached_role_policies(RoleName="process-order")["AttachedPolicies"]]
    assert attached == ["arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"], f"the role should have AWSLambdaSQSQueueExecutionRole; it has {attached}"


def test_function_configuration(acct):
    c = fn(acct)["Configuration"]
    assert c["Runtime"] == "python3.12" and c["Handler"] == "handler.handler", f"runtime/handler are {c['Runtime']}/{c['Handler']}"
    assert c["Timeout"] == 20, f"the timeout is {c['Timeout']}s, not 20 - the queue's 120 s must be at least six times it"
    assert c["MemorySize"] == 256, f"memory is {c['MemorySize']} MB, not 256"
    assert c.get("Environment", {}).get("Variables", {}).get("TABLE") == "orders", "TABLE=orders is not set"
    assert c["Role"].endswith(":role/process-order"), "the function should run as the process-order role"


def test_reserved_concurrency(acct):
    got = fn(acct).get("Concurrency", {}).get("ReservedConcurrentExecutions")
    assert got == 10, f"reserved concurrency is {got}, not 10"


def test_event_source_mapping(acct):
    lam = acct.client("lambda")
    maps = lam.list_event_source_mappings(FunctionName="process-order")["EventSourceMappings"]
    assert maps, "there is no event source mapping for process-order"
    m = maps[0]
    assert m["EventSourceArn"].endswith(":orders"), "the mapping should read from the orders queue"
    assert m.get("BatchSize") == 10, f"the batch size is {m.get('BatchSize')}, not 10"
    assert "ReportBatchItemFailures" in (m.get("FunctionResponseTypes") or []), "ReportBatchItemFailures is not on"
