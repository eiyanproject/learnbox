from netlab import build

CONFIGS = {"EDGE": "edge.ios", "ISP": "isp.ios"}


def configured():
    return build("edge", CONFIGS)


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_nat_boundary_is_marked():
    lab, _ = configured()
    edge = lab.device("EDGE")
    assert edge.interface("GigabitEthernet0/0").nat_side == "inside", "Gi0/0 faces the LAN"
    assert edge.interface("GigabitEthernet0/1").nat_side == "outside", "Gi0/1 faces the ISP"


def test_there_is_a_default_route():
    lab, _ = configured()
    route = lab.device("EDGE").lookup("8.8.8.8")
    assert route is not None, "EDGE has no route towards the internet"
    assert route.network.prefixlen == 0, "a default route is what sends unknown traffic to the ISP"


def test_overload_is_configured():
    lab, _ = configured()
    nat = lab.device("EDGE").nat
    assert nat.overload_interface, "no 'ip nat inside source list ... overload' statement"


def test_both_hosts_reach_the_server():
    lab, _ = configured()
    for pc in ("PC1", "PC2"):
        result = lab.ping(pc, "WEB")
        assert result.ok, f"{pc} cannot reach the server: {result.reason}"


def test_it_is_nat_doing_the_work():
    """Remove the translation and the reply has nowhere to go."""
    lab, errors = configured()
    lab.device("EDGE").nat.overload_interface = None
    result = lab.ping("PC1", "WEB")
    assert not result.ok
    assert "192.168.10" in result.reason
