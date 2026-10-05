from netlab import build

CONFIGS = {"R1": "r1.ios", "R2": "r2.ios"}


def configured():
    return build("two-routers", CONFIGS)


def test_both_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_addresses_match_the_table():
    lab, _ = configured()
    plan = {
        ("R1", "GigabitEthernet0/0"): ("192.168.1.1", "255.255.255.0"),
        ("R1", "GigabitEthernet0/1"): ("10.0.0.1", "255.255.255.252"),
        ("R2", "GigabitEthernet0/1"): ("10.0.0.2", "255.255.255.252"),
        ("R2", "GigabitEthernet0/0"): ("192.168.3.1", "255.255.255.0"),
    }
    for (dev, name), (ip, mask) in plan.items():
        iface = lab.device(dev).interface(name)
        assert (iface.ip, iface.mask) == (ip, mask), f"{dev} {name} should be {ip} {mask}"
        assert not iface.shutdown, f"{dev} {name} is administratively down"


def test_the_routers_reach_each_other():
    lab, _ = configured()
    result = lab.ping("R1", "R2")
    assert result.ok, f"the link itself is not working: {result.reason}"


def test_r1_routes_towards_pc2():
    lab, _ = configured()
    route = lab.device("R1").lookup("192.168.3.10")
    assert route is not None, "R1 has no route to 192.168.3.0/24"
    assert route.next_hop == "10.0.0.2", "R1's route should point at R2's end of the link"


def test_r2_routes_back():
    lab, _ = configured()
    route = lab.device("R2").lookup("192.168.1.10")
    assert route is not None, "R2 has no route back to 192.168.1.0/24"
    assert route.next_hop == "10.0.0.1"


def test_the_ping_works_in_both_directions():
    lab, _ = configured()
    for a, b in (("PC1", "PC2"), ("PC2", "PC1")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"
