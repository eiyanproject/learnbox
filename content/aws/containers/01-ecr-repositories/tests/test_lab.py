import json

import pytest

from awslab import lab, policy

PULL = {"ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:BatchCheckLayerAvailability"}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


@pytest.fixture(scope="module")
def repo(acct):
    ecr = acct.client("ecr")
    try:
        return ecr.describe_repositories(repositoryNames=["orders-api"])["repositories"][0]
    except ecr.exceptions.RepositoryNotFoundException:
        pytest.fail("there is no repository called orders-api")


def rules(acct):
    ecr = acct.client("ecr")
    try:
        text = ecr.get_lifecycle_policy(repositoryName="orders-api")["lifecyclePolicyText"]
    except ecr.exceptions.LifecyclePolicyNotFoundException:
        pytest.fail("orders-api has no lifecycle policy")
    return {r["rulePriority"]: r for r in json.loads(text).get("rules", [])}


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_repository_settings(repo):
    assert repo.get("imageTagMutability") == "IMMUTABLE", "tags are mutable - a tag could be pushed again with different content"
    assert repo.get("imageScanningConfiguration", {}).get("scanOnPush") is True, "scan on push is off"
    assert repo.get("encryptionConfiguration", {}).get("encryptionType") == "KMS", "the repository is not encrypted with KMS"


def test_untagged_images_expire_after_7_days(acct):
    r = rules(acct)
    assert 1 in r, "there is no lifecycle rule with priority 1"
    sel = r[1].get("selection", {})
    assert sel.get("tagStatus") == "untagged", "rule 1 does not select untagged images"
    assert (sel.get("countType"), sel.get("countUnit"), sel.get("countNumber")) == ("sinceImagePushed", "days", 7), "rule 1 should expire images 7 days after they are pushed"
    assert r[1].get("action", {}).get("type") == "expire", "rule 1 does not expire images"


def test_only_20_releases_are_kept(acct):
    r = rules(acct)
    assert 2 in r, "there is no lifecycle rule with priority 2"
    sel = r[2].get("selection", {})
    assert sel.get("tagStatus") == "tagged" and sel.get("tagPrefixList") == ["release-"], "rule 2 should select images tagged release-"
    assert (sel.get("countType"), sel.get("countNumber")) == ("imageCountMoreThan", 20), "rule 2 should keep the newest 20 (imageCountMoreThan 20)"
    assert r[2].get("action", {}).get("type") == "expire", "rule 2 does not expire images"


def test_prod_account_may_pull_and_nothing_more(acct):
    ecr = acct.client("ecr")
    try:
        doc = policy.load(ecr.get_repository_policy(repositoryName="orders-api")["policyText"])
    except ecr.exceptions.RepositoryPolicyNotFoundException:
        pytest.fail("orders-api has no repository policy")
    sts = [s for s in policy.statements(doc) if s.get("Sid") == "ProdPull"]
    assert sts, "there is no statement with Sid ProdPull"
    st = sts[0]
    principals = policy.as_list(st.get("Principal", {}).get("AWS"))
    assert any("111122223333" in p for p in principals), "ProdPull does not name account 111122223333"
    assert st.get("Effect") == "Allow", "ProdPull should allow"
    actions = set(policy.as_list(st.get("Action")))
    assert actions == PULL, f"ProdPull allows {sorted(actions)}, not exactly the three pull actions"


def test_registry_replicates_to_eu_west_1(acct):
    account = acct.client("sts").get_caller_identity()["Account"]
    cfg = acct.client("ecr").describe_registry().get("replicationConfiguration", {})
    dests = [d for r in cfg.get("rules", []) for d in r.get("destinations", [])]
    assert {"region": "eu-west-1", "registryId": account} in dests, "the registry does not replicate to eu-west-1 in this account"
