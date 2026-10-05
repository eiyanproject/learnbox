from netlab import build

CONFIGS = {"R1": "r1.ios", "R2": "r2.ios", "R3": "r3.ios"}

PLAN = {
    ("R1", "GigabitEthernet0/0"): ("172.16.1.1", "255.255.255.0"),
    ("R1", "GigabitEthernet0/1"): ("10.1.12.1", "255.255.255.252"),
    ("R2", "GigabitEthernet0/1"): ("10.1.12.2", "255.255.255.252"),
    ("R2", "GigabitEthernet0/2"): ("10.1.23.1", "255.255.255.252"),
    ("R3", "GigabitEthernet0/2"): ("10.1.23.2", "255.255.255.252"),
    ("R3", "GigabitEthernet0/0"): ("172.16.9.1", "255.255.255.0"),
}


def configured():
    return build("branch", CONFIGS)


def test_all_three_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_every_interface_matches_the_table():
    lab, _ = configured()
    for (dev, name), (ip, mask) in PLAN.items():
        iface = lab.device(dev).interface(name)
        assert (iface.ip, iface.mask) == (ip, mask), f"{dev} {name} should be {ip} {mask}"
        assert not iface.shutdown, f"{dev} {name} is administratively down"


def test_neighbours_reach_each_other():
    lab, _ = configured()
    for a, b in (("R1", "R2"), ("R2", "R3")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"


def test_the_end_routers_use_a_default_route():
    lab, _ = configured()
    for dev, hop in (("R1", "10.1.12.2"), ("R3", "10.1.23.1")):
        route = lab.device(dev).lookup("198.51.100.7")
        assert route is not None, f"{dev} has no default route"
        assert str(route.network) == "0.0.0.0/0", f"{dev} should reach unknown networks by a default route"
        assert route.next_hop == hop, f"{dev}'s default route should point at R2 ({hop})"


def test_r2_knows_both_lans():
    lab, _ = configured()
    r2 = lab.device("R2")
    for target, hop in (("172.16.1.10", "10.1.12.1"), ("172.16.9.10", "10.1.23.2")):
        route = r2.lookup(target)
        assert route is not None, f"R2 has no route to {target}"
        assert route.next_hop == hop, f"R2 should reach {target} by {hop}"


def test_pc1_and_the_server_reach_each_other():
    lab, _ = configured()
    for a, b in (("PC1", "SRV"), ("SRV", "PC1")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"


def test_the_path_crosses_all_three_routers():
    lab, _ = configured()
    assert lab.ping("PC1", "SRV").path == ["PC1", "R1", "R2", "R3", "SRV"]


def test_the_access_list_is_applied_outbound_towards_the_server():
    lab, _ = configured()
    r3 = lab.device("R3")
    assert "10" in r3.acls, "R3 has no access list numbered 10"
    assert r3.interface("GigabitEthernet0/0").acl_out == "10", "list 10 should be applied outbound on R3 g0/0"


def test_only_the_branch_lan_reaches_the_server():
    lab, _ = configured()
    result = lab.ping("R2", "SRV")
    assert not result.ok, "a ping from R2 itself should be stopped before the server"
    assert "access list 10" in result.reason, f"expected access list 10 to be the reason, got: {result.reason}"
    assert lab.ping("PC1", "SRV").ok, "the access list is blocking the branch LAN too"
