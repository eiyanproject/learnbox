from netlab import build

CONFIGS = {"SW1": "sw1.ios", "R1": "r1.ios"}


def configured():
    return build("router-on-a-stick", CONFIGS)


def test_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_link_to_the_router_is_a_trunk():
    lab, _ = configured()
    iface = lab.device("SW1").interface("GigabitEthernet0/1")
    assert iface.mode == "trunk", "the link to the router must carry both VLANs, so it is a trunk"


def test_the_physical_interface_is_up():
    lab, _ = configured()
    parent = lab.device("R1").interface("GigabitEthernet0/0")
    assert not parent.shutdown, "the physical interface is shut, which takes every subinterface down with it"


def test_each_subinterface_tags_its_vlan_and_holds_the_gateway():
    lab, _ = configured()
    r1 = lab.device("R1")
    for name, vlan, ip in (("GigabitEthernet0/0.10", 10, "10.0.10.1"),
                           ("GigabitEthernet0/0.20", 20, "10.0.20.1")):
        iface = r1.interface(name)
        assert iface.encapsulation_vlan == vlan, f"{name} needs 'encapsulation dot1Q {vlan}'"
        assert iface.ip == ip, f"{name} should have {ip}"
        assert iface.mask == "255.255.255.0", f"{name} wants a /24 mask"


def test_each_pc_reaches_its_gateway():
    lab, _ = configured()
    assert lab.ping("PC1", "10.0.10.1").ok, "PC1 cannot reach its gateway"
    assert lab.ping("PC2", "10.0.20.1").ok, "PC2 cannot reach its gateway"


def test_the_vlans_talk_through_the_router():
    lab, _ = configured()
    for a, b in (("PC1", "PC2"), ("PC2", "PC1")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"
    assert "R1" in lab.ping("PC1", "PC2").path, "the traffic should be routed by R1"
