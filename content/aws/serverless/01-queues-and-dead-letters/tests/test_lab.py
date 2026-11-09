import json

import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def attrs(acct, name):
    sqs = acct.client("sqs")
    try:
        url = sqs.get_queue_url(QueueName=name)["QueueUrl"]
    except sqs.exceptions.ClientError:
        pytest.fail(f"there is no queue called {name}")
    return sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])["Attributes"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_dlq_keeps_messages_for_14_days(acct):
    a = attrs(acct, "orders-dlq")
    assert a.get("MessageRetentionPeriod") == "1209600", f"orders-dlq keeps messages {a.get('MessageRetentionPeriod')}s, not 14 days (1209600)"


@pytest.mark.parametrize("key,want", [("VisibilityTimeout", "120"), ("ReceiveMessageWaitTimeSeconds", "20"), ("MessageRetentionPeriod", "345600")])
def test_orders_settings(acct, key, want):
    got = attrs(acct, "orders").get(key)
    assert got == want, f"orders has {key} = {got}, not {want}"


def test_orders_redrives_to_the_dlq(acct):
    a = attrs(acct, "orders")
    assert "RedrivePolicy" in a, "orders has no redrive policy"
    rp = json.loads(a["RedrivePolicy"])
    dlq = attrs(acct, "orders-dlq")["QueueArn"]
    assert rp.get("deadLetterTargetArn") == dlq, "the redrive policy does not point at orders-dlq"
    assert str(rp.get("maxReceiveCount")) == "5", f"maxReceiveCount is {rp.get('maxReceiveCount')}, not 5"


def test_payments_is_fifo_with_dedup(acct):
    a = attrs(acct, "payments.fifo")
    assert a.get("FifoQueue") == "true", "payments.fifo is not a FIFO queue"
    assert a.get("ContentBasedDeduplication") == "true", "content-based deduplication is off"


@pytest.mark.parametrize("name,count", [("orders", 2), ("payments.fifo", 1)])
def test_messages_were_sent(acct, name, count):
    got = int(attrs(acct, name).get("ApproximateNumberOfMessages", 0))
    assert got == count, f"{name} holds {got} messages, not {count}"
