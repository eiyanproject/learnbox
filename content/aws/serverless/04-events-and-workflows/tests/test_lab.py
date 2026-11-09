import json

import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def machine(acct):
    sfn = acct.client("stepfunctions")
    found = [m for m in sfn.list_state_machines()["stateMachines"] if m["name"] == "order-flow"]
    assert found, "there is no state machine called order-flow"
    return sfn.describe_state_machine(stateMachineArn=found[0]["stateMachineArn"])


def states(acct):
    d = json.loads(machine(acct)["definition"])
    assert d.get("StartAt") == "Charge", f"the workflow should start at Charge, not {d.get('StartAt')}"
    return d.get("States", {})


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_runs_as_its_role(acct):
    assert machine(acct)["roleArn"].endswith(":role/order-flow"), "order-flow should run as the order-flow role"


def test_charge_retries_and_catches(acct):
    s = states(acct)
    assert "Charge" in s, "there is no Charge state"
    c = s["Charge"]
    assert c.get("Type") == "Task" and c.get("Resource", "").endswith(":function:charge"), "Charge should be a Task calling the charge function"
    retry = [r for r in c.get("Retry", []) if "States.TaskFailed" in r.get("ErrorEquals", [])]
    assert retry, "Charge has no Retry for States.TaskFailed"
    assert retry[0].get("MaxAttempts") == 3, f"Charge retries {retry[0].get('MaxAttempts')} times, not 3"
    assert retry[0].get("BackoffRate") == 2, f"the backoff rate is {retry[0].get('BackoffRate')}, not 2"
    catch = [k for k in c.get("Catch", []) if "States.ALL" in k.get("ErrorEquals", [])]
    assert catch and catch[0].get("Next") == "Failed", "Charge should catch States.ALL and go to Failed"
    assert c.get("Next") == "CheckPaid", "after Charge comes CheckPaid"


def test_check_paid_chooses(acct):
    s = states(acct)
    assert s.get("CheckPaid", {}).get("Type") == "Choice", "CheckPaid should be a Choice state"
    ch = s["CheckPaid"]
    rules = [r for r in ch.get("Choices", []) if r.get("Variable") == "$.paid" and r.get("BooleanEquals") is True]
    assert rules and rules[0].get("Next") == "Ship", "CheckPaid should go to Ship when $.paid is true"
    assert ch.get("Default") == "Failed", "otherwise CheckPaid should go to Failed"


def test_ship_and_failed(acct):
    s = states(acct)
    ship = s.get("Ship", {})
    assert ship.get("Type") == "Task" and ship.get("Resource", "").endswith(":function:ship"), "Ship should be a Task calling the ship function"
    assert ship.get("End") is True, "Ship should end the run"
    assert s.get("Failed", {}).get("Type") == "Fail", "Failed should be a Fail state"


def test_nightly_rule_targets_the_workflow(acct):
    ev = acct.client("events")
    try:
        rule = ev.describe_rule(Name="nightly-orders")
    except ev.exceptions.ResourceNotFoundException:
        pytest.fail("there is no EventBridge rule called nightly-orders")
    assert rule.get("ScheduleExpression") == "cron(0 2 * * ? *)", f"the schedule is {rule.get('ScheduleExpression')}, not 02:00 UTC daily"
    targets = ev.list_targets_by_rule(Rule="nightly-orders")["Targets"]
    assert targets and targets[0]["Arn"] == machine(acct)["stateMachineArn"], "the rule should target order-flow"
    assert targets[0].get("RoleArn", "").endswith(":role/nightly-orders"), "the target needs the nightly-orders role to start the workflow"
