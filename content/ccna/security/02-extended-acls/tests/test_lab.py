from netlab import build

CONFIGS = {"EDGE": "edge.ios", "ISP": "isp.ios"}


def configured():
    return build("edge", CONFIGS)


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_named_list_exists():
    lab, _ = configured()
    assert "BLOCK_WEB" in lab.device("EDGE").acls, "no extended list named BLOCK_WEB"


def test_it_is_applied_inbound():
    lab, _ = configured()
    assert lab.device("EDGE").interface("GigabitEthernet0/0").acl_in == "BLOCK_WEB"


def test_the_rules_are_in_the_right_order():
    """A permit above the deny would make the deny unreachable."""
    lab, _ = configured()
    entries = lab.device("EDGE").acls["BLOCK_WEB"].entries
    assert entries, "the list has no rules"
    assert entries[0].action == "deny", "the specific deny has to come before the general permit"


def test_nobody_reaches_the_blocked_destination():
    lab, _ = configured()
    for pc in ("PC1", "PC2"):
        result = lab.ping(pc, "WEB")
        assert not result.ok, f"{pc} should not reach 8.8.8.8"
        assert "BLOCK_WEB" in result.reason


def test_other_destinations_still_work():
    lab, _ = configured()
    result = lab.ping("PC1", "203.0.113.1")
    assert result.ok, (
        "only 8.8.8.8 should be blocked - did you forget 'permit ip any any'? "
        f"({result.reason})"
    )
