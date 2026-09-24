from netlab import build


def configured():
    return build("one-router", {"R1": "r1.ios"})


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_lan_interface_is_up_and_addressed():
    lab, _ = configured()
    iface = lab.device("R1").interface("GigabitEthernet0/0")
    assert iface.ip == "192.168.1.1"
    assert not iface.shutdown


def test_a_pool_exists():
    lab, _ = configured()
    pools = lab.device("R1").dhcp_pools
    assert pools, "no 'ip dhcp pool' was configured"
    assert "LAN" in pools, f"expected a pool named LAN, found {list(pools)}"


def test_the_pool_covers_the_right_subnet():
    lab, _ = configured()
    pool = lab.device("R1").dhcp_pools["LAN"]
    assert pool.network is not None, "the pool has no network statement"
    assert str(pool.network) == "192.168.1.0/24"


def test_the_pool_hands_out_a_gateway():
    lab, _ = configured()
    pool = lab.device("R1").dhcp_pools["LAN"]
    assert pool.default_router == "192.168.1.1", (
        "without default-router the clients get an address and cannot leave the subnet"
    )


def test_the_pool_hands_out_dns():
    lab, _ = configured()
    assert lab.device("R1").dhcp_pools["LAN"].dns_server == "8.8.8.8"


def test_the_gateway_answers():
    lab, _ = configured()
    assert lab.ping("PC1", "R1").ok
