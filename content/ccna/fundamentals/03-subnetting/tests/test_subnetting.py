import pytest

from subnetting import broadcast_address, network_address, same_subnet, split, usable_hosts


@pytest.mark.parametrize(
    "ip, mask, expected",
    [
        ("192.168.1.10", "255.255.255.0", "192.168.1.0"),
        ("192.168.1.200", "255.255.255.192", "192.168.1.192"),
        ("10.5.17.9", "255.255.0.0", "10.5.0.0"),
        ("172.16.34.1", "255.255.255.252", "172.16.34.0"),
    ],
)
def test_network_address(ip, mask, expected):
    assert network_address(ip, mask) == expected


@pytest.mark.parametrize(
    "ip, mask, expected",
    [
        ("192.168.1.10", "255.255.255.0", "192.168.1.255"),
        ("192.168.1.200", "255.255.255.192", "192.168.1.255"),
        ("192.168.1.10", "255.255.255.192", "192.168.1.63"),
        ("10.5.17.9", "255.255.0.0", "10.5.255.255"),
    ],
)
def test_broadcast_address(ip, mask, expected):
    assert broadcast_address(ip, mask) == expected


@pytest.mark.parametrize(
    "prefix, expected",
    [(24, 254), (25, 126), (26, 62), (27, 30), (28, 14), (30, 2), (16, 65534)],
)
def test_usable_hosts(prefix, expected):
    assert usable_hosts(prefix) == expected


def test_usable_hosts_handles_the_two_exceptions():
    assert usable_hosts(31) == 2, "/31 has no network or broadcast address (RFC 3021)"
    assert usable_hosts(32) == 1, "/32 is a single host"


def test_same_subnet():
    assert same_subnet("192.168.1.10", "192.168.1.99", "255.255.255.0")
    assert not same_subnet("192.168.1.10", "192.168.2.10", "255.255.255.0")


def test_same_subnet_depends_on_the_mask():
    # The same pair is together under /24 and apart under /26.
    assert same_subnet("192.168.1.10", "192.168.1.99", "255.255.255.0")
    assert not same_subnet("192.168.1.10", "192.168.1.99", "255.255.255.192")


def test_split_into_four():
    assert split("192.168.1.0/24", 26) == [
        "192.168.1.0/26",
        "192.168.1.64/26",
        "192.168.1.128/26",
        "192.168.1.192/26",
    ]


def test_split_into_two():
    assert split("10.0.0.0/8", 9) == ["10.0.0.0/9", "10.128.0.0/9"]


def test_split_returns_strings():
    assert all(isinstance(s, str) for s in split("192.168.1.0/24", 25))
