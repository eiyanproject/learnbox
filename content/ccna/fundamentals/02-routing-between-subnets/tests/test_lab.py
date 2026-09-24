from netlab import build


def configured():
    return build("one-router", {"R1": "r1.ios"})


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_both_interfaces_are_addressed_and_up():
    lab, _ = configured()
    r1 = lab.device("R1")
    for name, ip in (("GigabitEthernet0/0", "192.168.1.1"), ("GigabitEthernet0/1", "192.168.2.1")):
        iface = r1.interface(name)
        assert iface.ip == ip, f"{name} should have {ip}, has {iface.ip}"
        assert iface.mask == "255.255.255.0", f"{name} needs the mask 255.255.255.0"
        assert not iface.shutdown, f"{name} is still administratively down"


def test_the_router_has_a_connected_route_to_each_subnet():
    lab, _ = configured()
    nets = {str(r.network) for r in lab.device("R1").routing_table() if r.source == "C"}
    assert "192.168.1.0/24" in nets
    assert "192.168.2.0/24" in nets


def test_pc1_reaches_pc2():
    lab, _ = configured()
    result = lab.ping("PC1", "PC2")
    assert result.ok, f"PC1 cannot reach PC2: {result.reason}"


def test_the_path_goes_through_the_router():
    lab, _ = configured()
    assert lab.ping("PC1", "PC2").path == ["PC1", "R1", "PC2"]


def test_no_static_routes_were_needed():
    lab, _ = configured()
    assert lab.device("R1").static_routes == [], (
        "connected routes are enough here - a static route is not needed"
    )
