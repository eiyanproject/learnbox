from arp import build_table, detect_conflict, detect_gateway_takeover

CLEAN = [("192.168.0.1", "aa:aa:aa:aa:aa:aa"), ("192.168.0.5", "bb:bb:bb:bb:bb:bb")]
SPOOF = CLEAN + [("192.168.0.1", "ee:ee:ee:ee:ee:ee")]


def test_build_table_maps_ip_to_mac():
    t = build_table(CLEAN)
    assert t["192.168.0.1"] == "aa:aa:aa:aa:aa:aa"
    assert t["192.168.0.5"] == "bb:bb:bb:bb:bb:bb"


def test_build_table_most_recent_wins():
    t = build_table(SPOOF)
    assert t["192.168.0.1"] == "ee:ee:ee:ee:ee:ee"


def test_no_conflict_in_clean_traffic():
    assert detect_conflict(CLEAN) == set()


def test_conflict_detected():
    assert detect_conflict(SPOOF) == {"192.168.0.1"}


def test_conflict_only_flags_the_contested_ip():
    traffic = SPOOF + [("192.168.0.5", "bb:bb:bb:bb:bb:bb")]
    assert detect_conflict(traffic) == {"192.168.0.1"}


def test_gateway_takeover_detected():
    assert detect_gateway_takeover(SPOOF, "192.168.0.1", "aa:aa:aa:aa:aa:aa")


def test_no_takeover_in_clean_traffic():
    assert not detect_gateway_takeover(CLEAN, "192.168.0.1", "aa:aa:aa:aa:aa:aa")


def test_takeover_ignores_other_ips():
    traffic = [("192.168.0.5", "cc:cc:cc:cc:cc:cc")]
    assert not detect_gateway_takeover(traffic, "192.168.0.1", "aa:aa:aa:aa:aa:aa")
