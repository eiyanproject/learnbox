from netlab import build


def configured():
    return build("l3-switch", {"SW1": "sw1.ios"})


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_ip_routing_is_enabled():
    lab, _ = configured()
    assert lab.device("SW1").ip_routing, (
        "without 'ip routing' the SVIs answer pings but never forward between VLANs"
    )


def test_both_svis_exist_with_the_right_addresses():
    lab, _ = configured()
    sw = lab.device("SW1")
    assert sw.interface("Vlan10").ip == "10.0.10.1"
    assert sw.interface("Vlan20").ip == "10.0.20.1"


def test_ports_are_in_their_vlans():
    lab, _ = configured()
    sw = lab.device("SW1")
    assert sw.interface("FastEthernet0/1").vlan == 10
    assert sw.interface("FastEthernet0/2").vlan == 20
    assert sw.interface("FastEthernet0/3").vlan == 10


def test_a_pc_can_reach_its_gateway():
    lab, _ = configured()
    assert lab.ping("PC1", "10.0.10.1").ok
    assert lab.ping("PC2", "10.0.20.1").ok


def test_inter_vlan_routing_works():
    lab, _ = configured()
    result = lab.ping("PC1", "PC2")
    assert result.ok, f"the switch is not routing between VLANs: {result.reason}"


def test_same_vlan_traffic_still_switches():
    lab, _ = configured()
    assert lab.ping("PC1", "PC3").ok


def test_there_is_no_router_in_this_topology():
    """The point of the lesson: the switch did all of it."""
    lab, _ = configured()
    assert lab.ping("PC1", "PC2").path == ["PC1", "SW1", "PC2"]
