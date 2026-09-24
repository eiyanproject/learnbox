from netlab import build

CONFIGS = {"EDGE": "edge.ios", "ISP": "isp.ios"}


def configured():
    return build("edge", CONFIGS)


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_access_list_exists():
    lab, _ = configured()
    assert "20" in lab.device("EDGE").acls, "no access list numbered 20"


def test_it_is_applied_inbound_on_the_lan_interface():
    lab, _ = configured()
    iface = lab.device("EDGE").interface("GigabitEthernet0/0")
    assert iface.acl_in == "20", "list 20 should be applied inbound on Gi0/0"


def test_pc2_is_blocked():
    lab, _ = configured()
    result = lab.ping("PC2", "WEB")
    assert not result.ok, "PC2 should not reach the internet"
    assert "20" in result.reason, f"expected access list 20 to be the reason, got: {result.reason}"


def test_pc1_still_works():
    lab, _ = configured()
    result = lab.ping("PC1", "WEB")
    assert result.ok, (
        "PC1 is blocked too - did you forget 'permit any' after the deny? "
        f"({result.reason})"
    )


def test_nat_was_not_broken():
    lab, _ = configured()
    assert lab.device("EDGE").nat.overload_interface, "the NAT configuration should still be there"
