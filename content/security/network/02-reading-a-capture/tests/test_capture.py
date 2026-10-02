from capture import parse_pcap, frame_endpoints, frame_payload, find_basic_auth
from capture_data import SAMPLE


def test_parse_pcap_counts_frames():
    assert len(parse_pcap(SAMPLE)) == 3


def test_endpoints_of_the_first_packet():
    frames = parse_pcap(SAMPLE)
    assert frame_endpoints(frames[0]) == ("192.168.0.50", "93.184.216.34", 51000, 80)


def test_endpoints_of_the_reply():
    frames = parse_pcap(SAMPLE)
    # The SYN-ACK goes the other way, ports swapped.
    assert frame_endpoints(frames[1]) == ("93.184.216.34", "192.168.0.50", 80, 51000)


def test_handshake_packets_have_no_payload():
    frames = parse_pcap(SAMPLE)
    assert frame_payload(frames[0]) == b""
    assert frame_payload(frames[1]) == b""


def test_the_request_has_a_payload():
    frames = parse_pcap(SAMPLE)
    assert b"GET /account HTTP/1.1" in frame_payload(frames[2])


def test_find_basic_auth_recovers_the_credentials():
    frames = parse_pcap(SAMPLE)
    assert find_basic_auth(frames) == "admin:s3cret"


def test_find_basic_auth_none_when_absent():
    # The first two frames carry no HTTP, so there is nothing to find in them.
    frames = parse_pcap(SAMPLE)
    assert find_basic_auth(frames[:2]) is None
