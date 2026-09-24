from netlab import build

CONFIGS = {"SW1": "sw1.ios", "SW2": "sw2.ios"}


def configured():
    return build("two-switches", CONFIGS)


def test_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_both_vlans_exist_on_both_switches():
    lab, _ = configured()
    for name in ("SW1", "SW2"):
        vlans = lab.device(name).vlans
        assert 10 in vlans and 20 in vlans, f"{name} is missing a VLAN"


def test_the_link_is_a_trunk_at_both_ends():
    lab, _ = configured()
    for name in ("SW1", "SW2"):
        iface = lab.device(name).interface("GigabitEthernet0/1")
        assert iface.mode == "trunk", f"{name} Gi0/1 must be a trunk, is {iface.mode}"


def test_vlan_10_spans_the_trunk():
    lab, _ = configured()
    result = lab.ping("PC1", "PC3")
    assert result.ok, f"PC1 cannot reach PC3 across the trunk: {result.reason}"


def test_vlan_20_spans_the_trunk():
    lab, _ = configured()
    result = lab.ping("PC2", "PC4")
    assert result.ok, f"PC2 cannot reach PC4 across the trunk: {result.reason}"


def test_the_vlans_stay_separate():
    lab, _ = configured()
    assert not lab.ping("PC1", "PC2"), "VLAN 10 must not reach VLAN 20"
    assert not lab.ping("PC1", "PC4")
