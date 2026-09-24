import pytest

from routing import beats, best_route, is_default, matching

CONNECTED = {"network": "192.168.1.0/24", "distance": 0, "metric": 0}
STATIC = {"network": "192.168.1.0/24", "distance": 1, "metric": 0}
OSPF = {"network": "192.168.1.0/24", "distance": 110, "metric": 2}
OSPF_FAR = {"network": "192.168.1.0/24", "distance": 110, "metric": 20}
SPECIFIC = {"network": "192.168.1.0/26", "distance": 120, "metric": 15}
DEFAULT = {"network": "0.0.0.0/0", "distance": 1, "metric": 0}


def test_matching_finds_every_containing_route():
    found = matching([CONNECTED, SPECIFIC, DEFAULT], "192.168.1.10")
    assert CONNECTED in found and SPECIFIC in found and DEFAULT in found


def test_matching_excludes_routes_that_do_not_contain_the_address():
    found = matching([CONNECTED, SPECIFIC, DEFAULT], "192.168.1.200")
    assert SPECIFIC not in found, "192.168.1.200 is outside /26"
    assert CONNECTED in found


def test_matching_nothing():
    assert matching([CONNECTED], "10.0.0.1") == []


def test_longest_prefix_wins_even_with_a_worse_distance():
    best = best_route([CONNECTED, SPECIFIC], "192.168.1.10")
    assert best == SPECIFIC, "a /26 at distance 120 still beats a /24 at distance 0"


def test_distance_decides_when_prefixes_are_equal():
    assert best_route([OSPF, STATIC], "192.168.1.10") == STATIC
    assert best_route([STATIC, CONNECTED], "192.168.1.10") == CONNECTED


def test_metric_decides_when_prefix_and_distance_are_equal():
    assert best_route([OSPF_FAR, OSPF], "192.168.1.10") == OSPF


def test_the_default_route_is_the_last_resort():
    assert best_route([DEFAULT, CONNECTED], "192.168.1.10") == CONNECTED
    assert best_route([DEFAULT, CONNECTED], "8.8.8.8") == DEFAULT


def test_no_match_returns_none():
    assert best_route([CONNECTED], "8.8.8.8") is None


def test_is_default():
    assert is_default(DEFAULT)
    assert not is_default(CONNECTED)


def test_beats_applies_the_same_order():
    assert beats(SPECIFIC, CONNECTED), "longer prefix"
    assert beats(STATIC, OSPF), "lower distance"
    assert beats(OSPF, OSPF_FAR), "lower metric"
    assert not beats(CONNECTED, SPECIFIC)
