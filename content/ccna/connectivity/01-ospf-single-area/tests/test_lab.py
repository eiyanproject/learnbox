from netlab import build

CONFIGS = {"R1": "r1.ios", "R2": "r2.ios"}


def configured():
    lab, errors = build("two-routers", CONFIGS)
    lab.converge_ospf()
    return lab, errors


def test_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_ospf_is_running_on_both_routers():
    lab, _ = configured()
    for name in ("R1", "R2"):
        assert lab.device(name).ospf is not None, f"{name} has no 'router ospf' configuration"


def test_no_static_routes_were_used():
    lab, _ = configured()
    for name in ("R1", "R2"):
        assert lab.device(name).static_routes == [], (
            f"{name} has a static route - this lesson is about letting OSPF do it"
        )


def test_each_router_learned_the_far_lan():
    lab, _ = configured()
    r1 = {str(r.network) for r in lab.device("R1").ospf_routes}
    r2 = {str(r.network) for r in lab.device("R2").ospf_routes}
    assert "192.168.3.0/24" in r1, "R1 never learned R2's LAN - check R2's network statements"
    assert "192.168.1.0/24" in r2, "R2 never learned R1's LAN - check R1's network statements"


def test_the_learned_route_points_at_the_neighbour():
    lab, _ = configured()
    route = lab.device("R1").lookup("192.168.3.10")
    assert route.source == "O", "the route to the far LAN should be learned by OSPF"
    assert route.next_hop == "10.0.0.2"


def test_the_ping_works_both_ways():
    lab, _ = configured()
    for a, b in (("PC1", "PC2"), ("PC2", "PC1")):
        result = lab.ping(a, b)
        assert result.ok, f"{a} cannot reach {b}: {result.reason}"
