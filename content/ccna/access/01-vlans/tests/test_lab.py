from netlab import build


def configured():
    return build("switched", {"SW1": "sw1.ios"})


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_both_vlans_exist():
    lab, _ = configured()
    vlans = lab.device("SW1").vlans
    assert 10 in vlans, "VLAN 10 was never created"
    assert 20 in vlans, "VLAN 20 was never created"


def test_ports_are_in_the_right_vlans():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port, vlan in (("FastEthernet0/1", 10), ("FastEthernet0/2", 20),
                       ("FastEthernet0/3", 10), ("FastEthernet0/4", 20)):
        iface = sw.interface(port)
        assert iface.vlan == vlan, f"{port} should be in VLAN {vlan}, is in {iface.vlan}"


def test_ports_are_access_ports():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in ("FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3", "FastEthernet0/4"):
        assert sw.interface(port).mode == "access", f"{port} should be an access port"


def test_same_vlan_still_reaches():
    lab, _ = configured()
    assert lab.ping("PC1", "PC3"), "PC1 and PC3 are both in VLAN 10"
    assert lab.ping("PC2", "PC4"), "PC2 and PC4 are both in VLAN 20"


def test_different_vlans_are_separated():
    lab, _ = configured()
    assert not lab.ping("PC1", "PC2"), "VLAN 10 must not reach VLAN 20"
    assert not lab.ping("PC3", "PC4")


def test_the_addresses_did_not_change():
    """The PCs are all still in 10.0.0.0/24: the separation is layer 2."""
    lab, _ = configured()
    assert lab.device("PC1").iface.ip == "10.0.0.11"
    assert lab.device("PC2").iface.ip == "10.0.0.12"
