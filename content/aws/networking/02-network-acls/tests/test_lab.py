import ipaddress

import pytest

from awslab import lab

PROTOCOLS = {"-1": "all", "6": "tcp", "17": "udp", "tcp": "tcp", "udp": "udp", "all": "all"}


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def subnets(acct):
    return acct.by_name(acct.client("ec2").describe_subnets()["Subnets"])


def acl_named(acct, name):
    found = [
        a for a in acct.client("ec2").describe_network_acls()["NetworkAcls"]
        if acct.tags(a.get("Tags")).get("Name") == name
    ]
    assert found, f"there is no network ACL named {name}"
    return found[0]


def decide(acl, egress, proto, port, addr):
    """What the ACL does with one packet: rules in number order, first match wins."""
    rules = sorted((e for e in acl["Entries"] if e["Egress"] == egress), key=lambda e: e["RuleNumber"])
    for e in rules:
        p = PROTOCOLS.get(str(e["Protocol"]), str(e["Protocol"]))
        if p not in ("all", proto):
            continue
        if p != "all" and e.get("PortRange"):
            if not e["PortRange"]["From"] <= port <= e["PortRange"]["To"]:
                continue
        if ipaddress.ip_address(addr) not in ipaddress.ip_network(e["CidrBlock"]):
            continue
        return e["RuleAction"], e["RuleNumber"]
    return "deny", "*"


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


@pytest.mark.parametrize("name", ["public-a", "public-b"])
def test_public_subnets_use_the_acl(acct, name):
    acl = acl_named(acct, "public")
    sid = subnets(acct)[name]["SubnetId"]
    assert any(a["SubnetId"] == sid for a in acl["Associations"]), f"{name} is not associated with the public ACL"


@pytest.mark.parametrize("name", ["private-a", "private-b"])
def test_private_subnets_are_left_alone(acct, name):
    acl = acl_named(acct, "public")
    sid = subnets(acct)[name]["SubnetId"]
    assert not any(a["SubnetId"] == sid for a in acl["Associations"]), f"{name} should keep the default ACL"


PACKETS = [
    # (description, egress, protocol, port, address, expected action)
    ("HTTPS from a customer", False, "tcp", 443, "8.8.8.8", "allow"),
    ("HTTPS from the blocked range", False, "tcp", 443, "198.51.100.7", "deny"),
    ("SSH from the office", False, "tcp", 22, "203.0.113.20", "allow"),
    ("SSH from anywhere else", False, "tcp", 22, "8.8.8.8", "deny"),
    ("plain HTTP", False, "tcp", 80, "8.8.8.8", "deny"),
    ("a reply to an instance's own HTTPS call", False, "tcp", 40000, "8.8.8.8", "allow"),
    ("a reply to a customer, to their ephemeral port", True, "tcp", 51515, "8.8.8.8", "allow"),
    ("an instance calling an HTTPS API", True, "tcp", 443, "8.8.8.8", "allow"),
    ("an instance sending SMTP", True, "tcp", 25, "8.8.8.8", "deny"),
]


@pytest.mark.parametrize("what,egress,proto,port,addr,want", PACKETS, ids=[p[0] for p in PACKETS])
def test_packet(acct, what, egress, proto, port, addr, want):
    got, rule = decide(acl_named(acct, "public"), egress, proto, port, addr)
    assert got == want, f"{what} ({'out' if egress else 'in'} {proto}/{port} {addr}) is {got}ed by rule {rule}; it should be {want}ed"


def test_the_deny_comes_first(acct):
    acl = acl_named(acct, "public")
    deny = [e for e in acl["Entries"] if not e["Egress"] and e["RuleAction"] == "deny" and e["CidrBlock"] == "198.51.100.0/24"]
    assert deny, "there is no inbound deny rule for 198.51.100.0/24"
    allows = [e["RuleNumber"] for e in acl["Entries"] if not e["Egress"] and e["RuleAction"] == "allow"]
    assert deny[0]["RuleNumber"] < min(allows), "the deny rule must have a lower number than every inbound allow, or an allow matches first"
