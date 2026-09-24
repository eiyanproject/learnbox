from netlab import build

CONFIGS = {"R1": "r1.ios", "R2": "r2.ios", "CORE": "core.ios"}
VIP = "192.168.1.254"


def configured():
    return build("redundant", CONFIGS)


def test_configs_are_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_both_routers_are_in_the_same_hsrp_group():
    lab, _ = configured()
    for name in ("R1", "R2"):
        groups = lab.device(name).interface("GigabitEthernet0/0").hsrp
        assert 1 in groups, f"{name} is not in HSRP group 1"
        assert groups[1].virtual_ip == VIP, f"{name} has the wrong virtual address"


def test_r1_is_the_active_router():
    lab, _ = configured()
    r1 = lab.device("R1").interface("GigabitEthernet0/0").hsrp[1]
    r2 = lab.device("R2").interface("GigabitEthernet0/0").hsrp[1]
    assert r1.priority > r2.priority, "R1 needs the higher priority to be active"
    assert lab._hsrp_owner(VIP).device.name == "R1"


def test_r1_preempts():
    lab, _ = configured()
    assert lab.device("R1").interface("GigabitEthernet0/0").hsrp[1].preempt, (
        "without preempt R1 stays standby after it recovers, even at priority 110"
    )


def test_the_virtual_address_answers():
    lab, _ = configured()
    result = lab.ping("PC1", VIP)
    assert result.ok, f"PC1 cannot reach its gateway: {result.reason}"


def test_the_pc_can_reach_the_server_through_the_active_router():
    lab, _ = configured()
    result = lab.ping("PC1", "SRV")
    assert result.ok, f"PC1 cannot reach the server: {result.reason}"
    assert "R1" in result.path, "traffic should be going via the active router"


def test_the_standby_takes_over_when_the_active_fails():
    """The point of HSRP: pull R1's LAN interface and the gateway still answers.

    Note what this does NOT claim. The gateway survives, so the hosts keep
    working locally and their ARP entry stays valid. Getting the *return*
    traffic to follow the failover needs a routing protocol upstream - CORE
    still has a static route pointing at R1. That is a real limitation of
    static routing, not a gap in the simulation.
    """
    lab, _ = configured()
    assert lab._hsrp_owner(VIP).device.name == "R1"
    lab.device("R1").interface("GigabitEthernet0/0").shutdown = True
    assert lab._hsrp_owner(VIP).device.name == "R2", "R2 should become active"
    result = lab.ping("PC1", VIP)
    assert result.ok, f"the virtual address stopped answering after failover: {result.reason}"
    assert "R2" in result.path, "the standby should now be forwarding"
