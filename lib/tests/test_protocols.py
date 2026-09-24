"""OSPF, ACLs, NAT, subinterfaces and SVIs.

Same principle as the layer 2/3 tests: each case is one where getting the
configuration slightly wrong must produce a failure, not a pass.
"""

import pytest

from netlab import Console, apply_config, topology
from netlab.protocols import wildcard_to_network


# ---------- wildcard masks ----------


@pytest.mark.parametrize(
    "addr, wildcard, expected",
    [
        ("10.0.0.0", "0.0.0.255", "10.0.0.0/24"),
        ("192.168.1.0", "0.0.0.0", "192.168.1.0/32"),
        ("10.0.0.0", "0.0.0.3", "10.0.0.0/30"),
        ("0.0.0.0", "255.255.255.255", "0.0.0.0/0"),
        ("172.16.0.0", "0.0.255.255", "172.16.0.0/16"),
    ],
)
def test_wildcard_to_network(addr, wildcard, expected):
    assert str(wildcard_to_network(addr, wildcard)) == expected


# ---------- OSPF ----------

R1_OSPF = """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
"""

R2_OSPF = """
interface GigabitEthernet0/0
 ip address 192.168.3.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
router ospf 1
 network 192.168.3.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
"""


def test_ospf_learns_the_far_subnet():
    lab = topology("two-routers")
    assert apply_config(lab, "R1", R1_OSPF) == []
    assert apply_config(lab, "R2", R2_OSPF) == []
    lab.converge_ospf()
    learned = {str(r.network): r.next_hop for r in lab.device("R1").ospf_routes}
    assert learned.get("192.168.3.0/24") == "10.0.0.2"


def test_ospf_gives_connectivity_without_static_routes():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_OSPF)
    apply_config(lab, "R2", R2_OSPF)
    assert lab.device("R1").static_routes == []
    assert lab.ping("PC1", "PC2")


def test_a_missing_network_statement_breaks_it():
    """The LAN is not advertised, so the other router never learns it."""
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_OSPF)
    apply_config(lab, "R2", R2_OSPF.replace(" network 192.168.3.0 0.0.0.255 area 0\n", ""))
    assert not lab.ping("PC1", "PC2")


def test_ospf_does_not_shadow_a_connected_route():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_OSPF)
    apply_config(lab, "R2", R2_OSPF)
    lab.converge_ospf()
    route = lab.device("R1").lookup("192.168.1.10")
    assert route.source == "C"


def test_a_static_route_beats_ospf_for_the_same_prefix():
    lab = topology("two-routers")
    apply_config(lab, "R1", R1_OSPF + "ip route 192.168.3.0 255.255.255.0 10.0.0.2\n")
    apply_config(lab, "R2", R2_OSPF)
    lab.converge_ospf()
    route = lab.device("R1").lookup("192.168.3.10")
    assert route.source == "S", "administrative distance 1 beats OSPF's 110"


def test_ospf_picks_a_path_round_a_triangle():
    lab = topology("triangle")
    common = """
interface GigabitEthernet0/{a}
 ip address {ip} {mask}
 no shutdown
"""
    apply_config(
        lab,
        "R1",
        common.format(a=0, ip="192.168.1.1", mask="255.255.255.0")
        + common.format(a=1, ip="10.0.12.1", mask="255.255.255.0")
        + "router ospf 1\n network 192.168.1.0 0.0.0.255 area 0\n network 10.0.12.0 0.0.0.255 area 0\n",
    )
    apply_config(
        lab,
        "R2",
        common.format(a=1, ip="10.0.12.2", mask="255.255.255.0")
        + common.format(a=2, ip="10.0.23.2", mask="255.255.255.0")
        + "router ospf 1\n network 10.0.12.0 0.0.0.255 area 0\n network 10.0.23.0 0.0.0.255 area 0\n",
    )
    apply_config(
        lab,
        "R3",
        common.format(a=0, ip="192.168.3.1", mask="255.255.255.0")
        + common.format(a=2, ip="10.0.23.3", mask="255.255.255.0")
        + "router ospf 1\n network 192.168.3.0 0.0.0.255 area 0\n network 10.0.23.0 0.0.0.255 area 0\n",
    )
    result = lab.ping("PC1", "PC3")
    assert result.ok, result.reason
    assert result.path == ["PC1", "R1", "R2", "R3", "PC3"]


# ---------- inter-VLAN routing ----------

SW_TRUNKED = """
vlan 10
vlan 20
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 20
interface GigabitEthernet0/1
 switchport mode trunk
"""

ROAS = """
interface GigabitEthernet0/0
 no shutdown
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
"""


def test_router_on_a_stick_routes_between_vlans():
    lab = topology("router-on-a-stick")
    assert apply_config(lab, "SW1", SW_TRUNKED) == []
    assert apply_config(lab, "R1", ROAS) == []
    assert lab.ping("PC1", "PC2")


def test_without_the_trunk_the_router_sees_one_vlan():
    lab = topology("router-on-a-stick")
    apply_config(lab, "SW1", SW_TRUNKED.replace(" switchport mode trunk", " switchport mode access"))
    apply_config(lab, "R1", ROAS)
    assert not lab.ping("PC1", "PC2")


def test_a_missing_subinterface_leaves_one_vlan_unrouted():
    lab = topology("router-on-a-stick")
    apply_config(lab, "SW1", SW_TRUNKED)
    apply_config(lab, "R1", ROAS.split("interface GigabitEthernet0/0.20")[0])
    assert not lab.ping("PC1", "PC2")


def test_wrong_encapsulation_vlan_breaks_it():
    lab = topology("router-on-a-stick")
    apply_config(lab, "SW1", SW_TRUNKED)
    apply_config(lab, "R1", ROAS.replace("encapsulation dot1Q 20", "encapsulation dot1Q 30"))
    assert not lab.ping("PC1", "PC2")


SVI_CONFIG = """
ip routing
vlan 10
vlan 20
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 20
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 10
interface Vlan10
 ip address 10.0.10.1 255.255.255.0
interface Vlan20
 ip address 10.0.20.1 255.255.255.0
"""


def test_layer3_switch_routes_between_svis():
    lab = topology("l3-switch")
    assert apply_config(lab, "SW1", SVI_CONFIG) == []
    assert lab.ping("PC1", "PC2")


def test_svis_without_ip_routing_do_not_route():
    lab = topology("l3-switch")
    apply_config(lab, "SW1", SVI_CONFIG.replace("ip routing\n", ""))
    assert not lab.ping("PC1", "PC2"), "'ip routing' is what makes it a layer 3 switch"


def test_same_vlan_still_switches_without_routing():
    lab = topology("l3-switch")
    apply_config(lab, "SW1", SVI_CONFIG.replace("ip routing\n", ""))
    assert lab.ping("PC1", "PC3")


# ---------- NAT ----------

EDGE_BASE = """
interface GigabitEthernet0/0
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 no shutdown
interface GigabitEthernet0/1
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
 no shutdown
ip route 0.0.0.0 0.0.0.0 203.0.113.1
"""

EDGE_PAT = EDGE_BASE + """
access-list 1 permit 192.168.10.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
"""

ISP = """
interface GigabitEthernet0/1
 ip address 203.0.113.1 255.255.255.252
 no shutdown
interface GigabitEthernet0/0
 ip address 8.8.8.1 255.255.255.0
 no shutdown
ip route 203.0.113.0 255.255.255.252 203.0.113.2
"""


def test_pat_lets_a_private_address_reach_the_internet():
    lab = topology("edge")
    assert apply_config(lab, "EDGE", EDGE_PAT) == []
    assert apply_config(lab, "ISP", ISP) == []
    assert lab.ping("PC1", "WEB")


def test_without_nat_the_reply_cannot_come_back():
    """The ISP has no route to a private address, which is the whole point."""
    lab = topology("edge")
    apply_config(lab, "EDGE", EDGE_BASE)
    apply_config(lab, "ISP", ISP)
    result = lab.ping("PC1", "WEB")
    assert not result
    assert "192.168.10" in result.reason


def test_static_nat_maps_one_host():
    lab = topology("edge")
    apply_config(lab, "EDGE", EDGE_BASE + "ip nat inside source static 192.168.10.11 203.0.113.2\n")
    apply_config(lab, "ISP", ISP)
    assert lab.ping("PC1", "WEB")


# ---------- ACLs ----------


def acl_lab(extra: str):
    lab = topology("edge")
    apply_config(lab, "EDGE", EDGE_PAT + extra)
    apply_config(lab, "ISP", ISP)
    return lab


def test_a_standard_acl_blocks_one_host():
    lab = acl_lab(
        """
access-list 20 deny 192.168.10.12 0.0.0.0
access-list 20 permit any
interface GigabitEthernet0/0
 ip access-group 20 in
"""
    )
    assert lab.ping("PC1", "WEB"), "PC1 is permitted"
    assert not lab.ping("PC2", "WEB"), "PC2 is denied"


def test_the_implicit_deny_blocks_everything_else():
    lab = acl_lab(
        """
access-list 30 permit 192.168.10.11 0.0.0.0
interface GigabitEthernet0/0
 ip access-group 30 in
"""
    )
    assert lab.ping("PC1", "WEB")
    assert not lab.ping("PC2", "WEB"), "no permit matches PC2, so the implicit deny does"


def test_an_acl_applied_outbound_filters_the_other_way():
    lab = acl_lab(
        """
access-list 40 deny 192.168.10.12 0.0.0.0
access-list 40 permit any
interface GigabitEthernet0/1
 ip access-group 40 out
"""
    )
    assert lab.ping("PC1", "WEB")
    assert not lab.ping("PC2", "WEB")


def test_an_extended_acl_can_match_the_destination():
    lab = acl_lab(
        """
ip access-list extended FILTER
 deny ip any host 8.8.8.8
 permit ip any any
interface GigabitEthernet0/0
 ip access-group FILTER in
"""
    )
    assert not lab.ping("PC1", "WEB"), "the destination is denied for everyone"


def test_show_access_lists_reports_what_was_configured():
    lab = acl_lab("access-list 50 permit 192.168.10.0 0.0.0.255\n")
    con = Console(lab, "EDGE")
    con.mode = "enable"
    out = con.run("show access-lists")
    assert "50" in out and "permit" in out
