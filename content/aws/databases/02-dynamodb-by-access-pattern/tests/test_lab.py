import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def table(acct):
    ddb = acct.client("dynamodb")
    try:
        return ddb.describe_table(TableName="orders")["Table"]
    except ddb.exceptions.ResourceNotFoundException:
        pytest.fail("there is no table called orders")


def keys(schema):
    return {k["KeyType"]: k["AttributeName"] for k in schema}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_keys_and_billing(acct):
    t = table(acct)
    assert keys(t["KeySchema"]) == {"HASH": "pk", "RANGE": "sk"}, f"the keys should be pk and sk; they are {keys(t['KeySchema'])}"
    types = {a["AttributeName"]: a["AttributeType"] for a in t["AttributeDefinitions"]}
    assert types.get("pk") == "S" and types.get("sk") == "S", "pk and sk should be strings"
    mode = (t.get("BillingModeSummary") or {}).get("BillingMode")
    assert mode == "PAY_PER_REQUEST", f"orders should be on-demand (PAY_PER_REQUEST), not {mode or 'provisioned'}"


def test_status_index(acct):
    gsis = {g["IndexName"]: g for g in table(acct).get("GlobalSecondaryIndexes", [])}
    assert "by-status" in gsis, "there is no global secondary index called by-status"
    g = gsis["by-status"]
    assert keys(g["KeySchema"]) == {"HASH": "status", "RANGE": "sk"}, f"by-status should be keyed on status and sk; it is {keys(g['KeySchema'])}"
    assert g["Projection"]["ProjectionType"] == "ALL", "by-status should project all attributes"


def test_ttl(acct):
    ttl = acct.client("dynamodb").describe_time_to_live(TableName="orders")["TimeToLiveDescription"]
    assert ttl.get("TimeToLiveStatus") in ("ENABLED", "ENABLING"), "TTL is off"
    assert ttl.get("AttributeName") == "expires_at", f"TTL uses {ttl.get('AttributeName')}, not expires_at"


def test_point_in_time_recovery(acct):
    d = acct.client("dynamodb").describe_continuous_backups(TableName="orders")["ContinuousBackupsDescription"]
    assert d["PointInTimeRecoveryDescription"]["PointInTimeRecoveryStatus"] == "ENABLED", "point-in-time recovery is off"


def query(acct, **kw):
    return acct.client("dynamodb").query(TableName="orders", **kw)["Items"]


def test_customer_one_has_three_orders(acct):
    items = query(acct, KeyConditionExpression="pk = :c", ExpressionAttributeValues={":c": {"S": "CUSTOMER#1"}})
    assert len(items) == 3, f"CUSTOMER#1 should have 3 orders; a query finds {len(items)}"
    for it in items:
        assert it["sk"]["S"].startswith("ORDER#"), f"sort keys should start with ORDER#: {it['sk']['S']}"
        assert "N" in it.get("total", {}), "each order needs a numeric total"


def test_customer_two_has_one_order(acct):
    items = query(acct, KeyConditionExpression="pk = :c", ExpressionAttributeValues={":c": {"S": "CUSTOMER#2"}})
    assert len(items) == 1, f"CUSTOMER#2 should have 1 order; a query finds {len(items)}"


@pytest.mark.parametrize("status", ["PLACED", "SHIPPED"])
def test_the_index_answers_by_status(acct, status):
    items = query(
        acct,
        IndexName="by-status",
        KeyConditionExpression="#s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": {"S": status}},
    )
    assert items, f"no order has status {status} - use both PLACED and SHIPPED"
