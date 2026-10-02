import struct
from packet import parse_ipv4, parse_tcp, tcp_flag_names, is_syn_only


def ipv4(src, dst, proto=6):
    return struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40, 0, 0, 64, proto, 0,
                       bytes(int(x) for x in src.split(".")),
                       bytes(int(x) for x in dst.split(".")))


def tcp(sp, dp, flags):
    return struct.pack("!HHIIBBHHH", sp, dp, 0, 0, 5 << 4, flags, 1024, 0, 0)


def test_ipv4_addresses():
    h = parse_ipv4(ipv4("192.168.0.50", "93.184.216.34"))
    assert h["src"] == "192.168.0.50"
    assert h["dst"] == "93.184.216.34"


def test_ipv4_version_and_length():
    h = parse_ipv4(ipv4("10.0.0.1", "10.0.0.2"))
    assert h["version"] == 4
    assert h["ihl"] == 20


def test_ipv4_protocol():
    assert parse_ipv4(ipv4("1.1.1.1", "2.2.2.2", proto=6))["protocol"] == 6
    assert parse_ipv4(ipv4("1.1.1.1", "2.2.2.2", proto=17))["protocol"] == 17


def test_tcp_ports():
    t = parse_tcp(tcp(51000, 80, 0x02))
    assert t["src_port"] == 51000
    assert t["dst_port"] == 80


def test_tcp_flags_syn():
    assert parse_tcp(tcp(1, 2, 0x02))["flags"] == {"SYN"}


def test_flag_names_syn_ack():
    assert tcp_flag_names(0x12) == {"SYN", "ACK"}


def test_flag_names_none():
    assert tcp_flag_names(0) == set()


def test_flag_names_psh_ack():
    assert tcp_flag_names(0x18) == {"PSH", "ACK"}


def test_flag_names_all():
    assert tcp_flag_names(0x3F) == {"FIN", "SYN", "RST", "PSH", "ACK", "URG"}


def test_is_syn_only_true():
    assert is_syn_only(0x02)


def test_is_syn_only_false_for_syn_ack():
    assert not is_syn_only(0x12)


def test_is_syn_only_false_for_nothing():
    assert not is_syn_only(0)
