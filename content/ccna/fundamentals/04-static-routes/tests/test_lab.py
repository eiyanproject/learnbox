from netlab import build

CONFIGS = {"R1": "r1.ios", "R2": "r2.ios"}


def configured():
    return build("two-routers", CONFIGS)


def test_both_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_link_between_the_routers_is_a_slash_30():
    lab, _ = configured()
    for dev, ip in (("R1", "10.0.0.1"), ("R2", "10.0.0.2")):
        iface = lab.device(dev).interface("GigabitEthernet0/1")
        assert iface.ip == ip, f"{dev} g0/1 should be {ip}"
        assert iface.mask == "255.255.255.252", f"{dev} g0/1 wants a /30 mask (255.255.255.252)"
        assert not iface.shutdown, f"{dev} g0/1 is administratively down"


def test_the_lan_interfaces_are_addressed():
    lab, _ = configured()
    assert lab.device("R1").interface("GigabitEthernet0/0").ip == "192.168.1.1"
    assert lab.device("R2").interface("GigabitEthernet0/0").ip == "192.168.3.1"


def test_the_routers_can_reach_each_other_across_the_link():
    lab, _ = configured()
    result = lab.ping("R1", "R2")
    assert result.ok, f"the link itself is not working: {result.reason}"


def test_r1_has_a_route_towards_the_far_lan():
    lab, _ = configured()
    route = lab.device("R1").lookup("192.168.3.10")
    assert route is not None, "R1 has no route to 192.168.3.0/24"
    assert route.next_hop == "10.0.0.2", "R1's route should point at R2's link address"


def test_r2_has_a_route_back():
    """The half everyone forgets: without this the replies are dropped."""
    lab, _ = configured()
    route = lab.device("R2").lookup("192.168.1.10")
    assert route is not None, "R2 has no route back to 192.168.1.0/24 - the reply has nowhere to go"
    assert route.next_hop == "10.0.0.1"


def test_the_ping_works_in_both_directions():
    lab, _ = configured()
    for a, b in (("PC1", "PC2"), ("PC2", "PC1")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"


def test_the_path_crosses_both_routers():
    lab, _ = configured()
    assert lab.ping("PC1", "PC2").path == ["PC1", "R1", "R2", "PC2"]
