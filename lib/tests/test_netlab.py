"""Tests for the simulator. Every lesson's grading rests on these being right.

The cases that matter are the ones where a naive simulator says "reachable"
and real kit does not: an interface left shut, a VLAN that does not span the
trunk, and a route that exists in one direction only.
"""

import pytest

from netlab import Console, Lab, apply_config, topology, topology_names


# ---------- topologies ship unconfigured ----------


def test_every_topology_builds():
    for name in topology_names():
        lab = topology(name)
        assert lab.devices, f"{name} has no devices"


def test_router_interfaces_start_shut():
    lab = topology("one-router")
    r1 = lab.device("R1")
    assert all(i.shutdown for i in r1.interfaces.values())
    assert not lab.ping("PC1", "PC2")


# ---------- layer 3 ----------


ONE_ROUTER = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
"""


def test_configured_router_routes_between_its_subnets():
    lab = topology("one-router")
    assert apply_config(lab, "R1", ONE_ROUTER) == []
    assert lab.ping("PC1", "PC2")


def test_forgetting_no_shutdown_leaves_it_unreachable():
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER.replace(" no shutdown\n", "", 1))
    result = lab.ping("PC1", "PC2")
    assert not result
    assert "down" in result.reason or "not reachable" in result.reason


def test_wrong_subnet_on_the_router_breaks_the_gateway():
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER.replace("192.168.1.1", "192.168.9.1"))
    assert not lab.ping("PC1", "PC2")


def test_traceroute_lists_each_hop():
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER)
    hops = lab.traceroute("PC1", "PC2")
    assert [h.name for h in hops] == ["R1", "PC2"]


# ---------- the asymmetric-route trap ----------

R1_ONLY = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
ip route 192.168.3.0 255.255.255.0 10.0.0.2
"""

R2_ONLY = """
interface GigabitEthernet0/0
 ip address 192.168.3.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
"""


def test_a_route_one_way_only_is_not_reachable():
    """R1 knows how to reach PC2's subnet; R2 has no route back to PC1's."""
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_ONLY)
    apply_config(lab, "R2", R2_ONLY)
    result = lab.ping("PC1", "PC2")
    assert not result, "a one-way path must not count as reachable"
    assert "reply" in result.reason


def test_both_routes_present_is_reachable():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_ONLY)
    apply_config(lab, "R2", R2_ONLY + "ip route 192.168.1.0 255.255.255.0 10.0.0.1\n")
    assert lab.ping("PC1", "PC2")


def test_default_route_also_works():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_ONLY)
    apply_config(lab, "R2", R2_ONLY + "ip route 0.0.0.0 0.0.0.0 10.0.0.1\n")
    assert lab.ping("PC1", "PC2")


def test_longest_prefix_wins_over_the_default_route():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_ONLY)
    apply_config(lab, "R2", R2_ONLY + "ip route 0.0.0.0 0.0.0.0 10.0.0.1\n")
    r2 = lab.device("R2")
    route = r2.lookup("192.168.3.10")
    assert route.prefix_len == 24 and route.source == "C"


# ---------- layer 2 ----------


def test_one_switch_is_one_broadcast_domain_by_default():
    lab = topology("switched")
    assert lab.ping("PC1", "PC2")


def test_different_vlans_cannot_reach_each_other():
    lab = topology("switched")
    apply_config(
        lab,
        "SW1",
        """
vlan 10
vlan 20
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 20
""",
    )
    assert not lab.ping("PC1", "PC2"), "VLAN 10 and VLAN 20 must be separated"
    # Fa0/3 was never touched, so PC3 is still in VLAN 1 - which is a third
    # broadcast domain, not a shared one. Moving one port moves one host.
    assert not lab.ping("PC1", "PC3"), "VLAN 10 and the default VLAN 1 are separate too"
    assert lab.ping("PC3", "PC4"), "the two untouched ports are both still VLAN 1"


def test_same_vlan_still_reaches():
    lab = topology("switched")
    apply_config(
        lab,
        "SW1",
        """
vlan 10
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
""",
    )
    assert lab.ping("PC1", "PC2")


ACCESS_PORTS = """
vlan 10
vlan 20
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 20
"""


def test_vlan_does_not_cross_an_access_link_between_switches():
    lab = topology("two-switches")
    apply_config(lab, "SW1", ACCESS_PORTS)
    apply_config(lab, "SW2", ACCESS_PORTS)
    assert not lab.ping("PC1", "PC3"), "without a trunk the VLAN does not span the switches"


def test_a_trunk_carries_the_vlan_between_switches():
    trunk = "\ninterface GigabitEthernet0/1\n switchport mode trunk\n"
    lab = topology("two-switches")
    apply_config(lab, "SW1", ACCESS_PORTS + trunk)
    apply_config(lab, "SW2", ACCESS_PORTS + trunk)
    assert lab.ping("PC1", "PC3"), "both in VLAN 10 across a trunk"
    assert not lab.ping("PC1", "PC4"), "still different VLANs"


def test_pruning_a_vlan_off_the_trunk_blocks_it():
    lab = topology("two-switches")
    trunk = "\ninterface GigabitEthernet0/1\n switchport mode trunk\n switchport trunk allowed vlan 20\n"
    apply_config(lab, "SW1", ACCESS_PORTS + trunk)
    apply_config(lab, "SW2", ACCESS_PORTS + trunk)
    assert not lab.ping("PC1", "PC3"), "VLAN 10 is not allowed on the trunk"
    assert lab.ping("PC2", "PC4"), "VLAN 20 is"


# ---------- the CLI ----------


def test_modes_are_enforced():
    lab = topology("one-router")
    con = Console(lab, "R1")
    assert con.prompt == "R1>"
    # An address cannot be set without entering interface configuration.
    assert "Invalid" in con.run("ip address 1.1.1.1 255.255.255.0")
    con.run("enable")
    assert con.prompt == "R1#"
    con.run("configure terminal")
    assert con.prompt == "R1(config)#"
    con.run("interface g0/0")
    assert con.prompt == "R1(config-if)#"
    con.run("exit")
    assert con.prompt == "R1(config)#"
    con.run("end")
    assert con.prompt == "R1#"


def test_hostname_changes_the_prompt():
    lab = topology("one-router")
    con = Console(lab, "R1")
    con.run("enable")
    con.run("configure terminal")
    con.run("hostname Edge")
    assert con.prompt == "Edge(config)#"


def test_abbreviations_are_accepted():
    lab = topology("one-router")
    assert apply_config(lab, "R1", "int g0/0\n ip address 192.168.1.1 255.255.255.0\n no shut\n") != []
    # "no shut" is not accepted, but "no shutdown" is:
    lab2 = topology("one-router")
    assert apply_config(lab2, "R1", "int g0/0\n ip address 192.168.1.1 255.255.255.0\n no shutdown\n") == []


def test_a_bad_command_is_reported_not_ignored():
    lab = topology("one-router")
    errors = apply_config(lab, "R1", "interface g0/0\n ip adress 1.1.1.1 255.255.255.0\n")
    assert errors, "a typo must be reported"
    assert "adress" in errors[0]


def test_invalid_interface_is_rejected():
    lab = topology("one-router")
    errors = apply_config(lab, "R1", "interface g9/9\n")
    assert errors


def test_show_ip_interface_brief_reports_status():
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER)
    con = Console(lab, "R1")
    con.mode = "enable"
    out = con.run("show ip interface brief")
    assert "192.168.1.1" in out and "192.168.2.1" in out
    assert "administratively down" not in out


def test_show_ip_route_lists_connected_and_static():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_ONLY)
    con = Console(lab, "R1")
    con.mode = "enable"
    out = con.run("show ip route")
    assert "C        192.168.1.0/24" in out
    assert "S        192.168.3.0/24 [1/0] via 10.0.0.2" in out


def test_ping_from_the_console_reports_like_ios():
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER)
    con = Console(lab, "R1")
    con.mode = "enable"
    assert "!!!!!" in con.run("ping 192.168.1.10")
    assert "....." in con.run("ping 10.9.9.9")


def test_running_config_round_trips():
    """A config read back out must rebuild the same working network."""
    lab = topology("one-router")
    apply_config(lab, "R1", ONE_ROUTER)
    con = Console(lab, "R1")
    con.mode = "enable"
    dumped = con.running_config()

    fresh = topology("one-router")
    assert apply_config(fresh, "R1", dumped) == []
    assert fresh.ping("PC1", "PC2")
