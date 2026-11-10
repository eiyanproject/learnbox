import json
import os

import pytest

from awslab import lab, policy

ADMIN_ONLY = ["kms:ScheduleKeyDeletion", "kms:DisableKey", "kms:PutKeyPolicy", "kms:CancelKeyDeletion"]
CRYPTO = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:ReEncryptFrom"]


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def key(acct):
    kms = acct.client("kms")
    try:
        meta = kms.describe_key(KeyId="alias/orders")["KeyMetadata"]
    except kms.exceptions.NotFoundException:
        pytest.fail("there is no key behind alias/orders")
    return meta


@pytest.fixture(scope="module")
def key_policy(acct, key):
    return json.loads(acct.client("kms").get_key_policy(KeyId=key["KeyId"], PolicyName="default")["Policy"])


def role_arn(acct, name):
    iam = acct.client("iam")
    try:
        return iam.get_role(RoleName=name)["Role"]["Arn"]
    except iam.exceptions.NoSuchEntityException:
        pytest.fail(f"there is no role called {name}")


def for_principal(key_policy, arn):
    """The key policy's statements that name this principal."""
    out = []
    for st in policy.as_list(key_policy.get("Statement")):
        principals = st.get("Principal", {})
        aws = policy.as_list(principals.get("AWS")) if isinstance(principals, dict) else [principals]
        if arn in aws:
            out.append(st)
    return [{"Statement": out}]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_key_is_customer_managed(key):
    assert key.get("KeyManager") == "CUSTOMER", "alias/orders should point at a customer managed key"
    assert key.get("Description") == "orders data", f"the key is described as {key.get('Description')!r}, not 'orders data'"


def test_rotation_is_on(acct, key):
    assert acct.client("kms").get_key_rotation_status(KeyId=key["KeyId"])["KeyRotationEnabled"], "automatic rotation is off"


def test_policy_delegates_to_the_account(acct, key_policy):
    root = f"arn:aws:iam::{acct.client('sts').get_caller_identity()['Account']}:root"
    d = policy.decide(for_principal(key_policy, root), "kms:PutKeyPolicy")
    assert d.allowed, "no statement lets the account (its root ARN) use kms:* - without it, IAM policies cannot grant access and you risk locking the key"


def test_key_admin_manages_but_cannot_decrypt(acct, key_policy):
    docs = for_principal(key_policy, role_arn(acct, "key-admin"))
    for action in ADMIN_ONLY:
        assert policy.decide(docs, action).allowed, f"key-admin cannot {action}"
    for action in CRYPTO:
        assert not policy.decide(docs, action).allowed, f"key-admin can {action} - administrators should not be able to read the data"


def test_orders_app_uses_the_key_only_with_its_context(acct, key_policy):
    docs = for_principal(key_policy, role_arn(acct, "orders-app"))
    assert docs[0]["Statement"], "the key policy has no statement for orders-app"
    for action in ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]:
        ok = policy.decide(docs, action, context={"kms:EncryptionContext:app": "orders"}).allowed
        assert ok, f"orders-app cannot {action} with the context app=orders"
    for action in ["kms:Decrypt", "kms:GenerateDataKey"]:
        other = policy.decide(docs, action, context={"kms:EncryptionContext:app": "billing"})
        assert not other.allowed, f"orders-app can {action} with app=billing - add the kms:EncryptionContext:app condition"
    for action in ADMIN_ONLY:
        assert not policy.decide(docs, action, context={"kms:EncryptionContext:app": "orders"}).allowed, f"orders-app can {action}"


def test_reporting_has_a_decrypt_only_grant(acct, key):
    grants = acct.client("kms").list_grants(KeyId=key["KeyId"])["Grants"]
    mine = [g for g in grants if g.get("GranteePrincipal") == role_arn(acct, "reporting")]
    assert mine, "no grant names the reporting role as grantee"
    g = mine[0]
    assert g.get("Name") == "reporting-read", f"the grant is called {g.get('Name')!r}, not reporting-read"
    assert g.get("Operations") == ["Decrypt"], f"the grant allows {g.get('Operations')}, not just Decrypt"
    subset = (g.get("Constraints") or {}).get("EncryptionContextSubset")
    assert subset == {"app": "orders"}, f"the grant's encryption context constraint is {subset}, not app=orders"


def test_encrypted_data_key_was_saved_and_decrypts_with_its_context(acct, key):
    assert os.path.exists("orders.key.enc"), "orders.key.enc was not written"
    blob = open("orders.key.enc", "rb").read()
    assert blob, "orders.key.enc is empty"
    kms = acct.client("kms")
    try:
        out = kms.decrypt(CiphertextBlob=blob, EncryptionContext={"app": "orders"})
    except Exception as e:
        pytest.fail(f"orders.key.enc does not decrypt with the context app=orders ({type(e).__name__}) - save the CiphertextBlob, base64-decoded")
    assert out["KeyId"] == key["Arn"], "orders.key.enc was encrypted under a different key"
    assert len(out["Plaintext"]) == 32, "the data key is not 256 bits (AES_256)"


def test_global_key_is_multi_region_with_a_replica_in_eu_west_1(acct, key_policy):
    kms = acct.client("kms")
    try:
        g = kms.describe_key(KeyId="alias/orders-global")["KeyMetadata"]
    except kms.exceptions.NotFoundException:
        pytest.fail("there is no key behind alias/orders-global")
    assert g.get("MultiRegion") is True, "the orders-global key is not multi-Region: create it with --multi-region"
    assert json.loads(kms.get_key_policy(KeyId=g["KeyId"], PolicyName="default")["Policy"]) == key_policy, "orders-global should have the same key policy as alias/orders"
    try:
        rep = acct.client("kms", region="eu-west-1").describe_key(KeyId=g["KeyId"])["KeyMetadata"]
    except Exception:
        pytest.fail("there is no replica of the orders-global key in eu-west-1")
    assert rep.get("MultiRegionConfiguration", {}).get("MultiRegionKeyType") == "REPLICA", "the eu-west-1 key is not a replica"
