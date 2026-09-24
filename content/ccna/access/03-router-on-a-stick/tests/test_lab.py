from netlab import build

CONFIGS = {"SW1": "sw1.ios", "R1": "r1.ios"}


def configured():
    return build("router-on-a-stick", CONFIGS)


def test_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_switch_link_to_the_router_is_a_trunk():
    lab, _ = configured()
    iface = lab.device("SW1").interface("GigabitEthernet0/1")
    assert iface.mode == "trunk", "the link to the router must carry both VLANs, so it is a trunk"


def test_the_physical_interface_is_up():
    lab, _ = configured()
    parent = lab.device("R1").interface("GigabitEthernet0/0")
    assert not parent.shutdown, "the physical interface needs 'no shutdown' or every subinterface is down"


def test_each_subinterface_has_the_right_encapsulation_and_address():
    lab, _ = configured()
    r1 = lab.device("R1")
    for name, vlan, ip in (("GigabitEthernet0/0.10", 10, "10.0.10.1"),
                           ("GigabitEthernet0/0.20", 20, "10.0.20.1")):
        iface = r1.interface(name)
        assert iface.encapsulation_vlan == vlan, f"{name} needs 'encapsulation dot1Q {vlan}'"
        assert iface.ip == ip, f"{name} should have {ip}"


def test_each_pc_can_reach_its_own_gateway():
    lab, _ = configured()
    assert lab.ping("PC1", "10.0.10.1").ok, "PC1 cannot reach its gateway"
    assert lab.ping("PC2", "10.0.20.1").ok, "PC2 cannot reach its gateway"


def test_the_two_vlans_can_now_reach_each_other():
    lab, _ = configured()
    result = lab.ping("PC1", "PC2")
    assert result.ok, f"inter-VLAN routing is not working: {result.reason}"


def test_the_path_goes_via_the_router():
    lab, _ = configured()
    assert lab.ping("PC1", "PC2").path == ["PC1", "R1", "PC2"]


def test_no_static_routes_were_needed():
    lab, _ = configured()
    assert lab.device("R1").static_routes == [], "both subnets are connected; no static route is needed"
