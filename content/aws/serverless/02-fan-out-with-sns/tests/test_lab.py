import json

import pytest

from awslab import lab, policy


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def topic_arn(acct):
    arns = [t["TopicArn"] for t in acct.client("sns").list_topics()["Topics"] if t["TopicArn"].endswith(":order-events")]
    assert arns, "there is no topic called order-events"
    return arns[0]


def queue(acct, name):
    sqs = acct.client("sqs")
    try:
        url = sqs.get_queue_url(QueueName=name)["QueueUrl"]
    except sqs.exceptions.ClientError:
        pytest.fail(f"there is no queue called {name}")
    return url, sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])["Attributes"]


def subscriptions(acct):
    sns = acct.client("sns")
    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn(acct))["Subscriptions"]
    return {s["Endpoint"].rsplit(":", 1)[-1]: sns.get_subscription_attributes(SubscriptionArn=s["SubscriptionArn"])["Attributes"] for s in subs}


@pytest.fixture(scope="module")
def received(acct):
    """Every message each queue holds, read once (reading hides them)."""
    out = {}
    for name in ("billing", "shipping"):
        url, _ = queue(acct, name)
        msgs = []
        for _ in range(5):
            batch = acct.client("sqs").receive_message(QueueUrl=url, MaxNumberOfMessages=10, WaitTimeSeconds=1).get("Messages", [])
            if not batch:
                break
            msgs += [m["Body"] for m in batch]
        out[name] = msgs
    return out


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


@pytest.mark.parametrize("name", ["billing", "shipping"])
def test_queue_policy_lets_only_the_topic_in(acct, name):
    _, a = queue(acct, name)
    assert "Policy" in a, f"{name} has no access policy, so SNS cannot deliver to it"
    sts = [s for s in policy.statements(a["Policy"]) if s.get("Effect") == "Allow"]
    assert sts, f"{name}'s policy allows nothing"
    for s in sts:
        assert s.get("Principal") in ({"Service": "sns.amazonaws.com"}, {"Service": ["sns.amazonaws.com"]}), f"{name}'s policy should allow the SNS service, not {s.get('Principal')}"
        assert "sqs:SendMessage" in policy.as_list(s.get("Action")), f"{name}'s policy should allow sqs:SendMessage"
        src = (s.get("Condition") or {}).get("ArnEquals", {}).get("aws:SourceArn") or (s.get("Condition") or {}).get("ArnLike", {}).get("aws:SourceArn")
        assert policy.as_list(src) == [topic_arn(acct)], f"{name}'s policy should be limited to order-events with aws:SourceArn"


def test_both_queues_subscribed_with_raw_delivery(acct):
    subs = subscriptions(acct)
    for name in ("billing", "shipping"):
        assert name in subs, f"{name} is not subscribed to order-events"
        assert subs[name].get("RawMessageDelivery") == "true", f"{name}'s subscription does not use raw delivery"


def test_shipping_filters_on_order_paid(acct):
    fp = subscriptions(acct).get("shipping", {}).get("FilterPolicy")
    assert fp, "shipping's subscription has no filter policy"
    assert json.loads(fp) == {"event": ["order_paid"]}, f"shipping's filter policy is {fp}, not event = order_paid"
    assert not subscriptions(acct).get("billing", {}).get("FilterPolicy"), "billing should get every event - no filter policy"


def test_billing_got_both_events(acct, received):
    assert len(received["billing"]) == 2, f"billing should hold 2 messages; it holds {len(received['billing'])}"
    assert all(not b.lstrip().startswith('{"Type"') for b in received["billing"]), "billing's messages are wrapped in SNS envelopes - raw delivery is off"


def test_shipping_got_only_the_paid_event(acct, received):
    assert len(received["shipping"]) == 1, f"shipping should hold 1 message; it holds {len(received['shipping'])}"
    assert "order_paid" in received["shipping"][0], "shipping got the wrong event"
