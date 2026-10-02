from scan import open_ports, detect_scan


def test_open_ports_finds_syn_ack():
    replies = [(22, {"SYN", "ACK"}), (23, {"RST"}), (80, {"SYN", "ACK"})]
    assert open_ports(replies) == [22, 80]


def test_open_ports_sorted():
    replies = [(443, {"SYN", "ACK"}), (22, {"SYN", "ACK"})]
    assert open_ports(replies) == [22, 443]


def test_open_ports_none_open():
    assert open_ports([(22, {"RST"}), (80, {"RST"})]) == []


def test_open_ports_ignores_filtered():
    # A filtered port gives no reply, so it is simply not in the list.
    assert open_ports([(22, {"SYN", "ACK"})]) == [22]


def test_detect_scan_flags_the_scanner():
    probes = [("10.0.0.9", p) for p in range(1, 30)]
    assert "10.0.0.9" in detect_scan(probes)


def test_detect_scan_ignores_normal_clients():
    # A normal client touching a couple of ports is well under the threshold.
    normal = [("10.0.0.5", 80), ("10.0.0.5", 443), ("10.0.0.6", 22)]
    assert detect_scan(normal) == set()


def test_detect_scan_respects_threshold():
    probes = [("1.2.3.4", p) for p in range(5)]
    assert detect_scan(probes, threshold=3) == {"1.2.3.4"}
    assert detect_scan(probes, threshold=10) == set()


def test_detect_scan_counts_distinct_ports_only():
    # The same port hit repeatedly is not a scan.
    probes = [("9.9.9.9", 80) for _ in range(50)]
    assert detect_scan(probes) == set()


def test_detect_scan_finds_several_scanners():
    probes = [("a", p) for p in range(20)] + [("b", p) for p in range(20)]
    assert detect_scan(probes) == {"a", "b"}
