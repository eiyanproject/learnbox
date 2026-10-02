import struct
from dns import parse_header, accept_response


def header(ident, flags, qd=1, an=0):
    return struct.pack("!HHHHHH", ident, flags, qd, an, 0, 0)


def test_parse_id():
    assert parse_header(header(0x1234, 0x0100))["id"] == 0x1234


def test_parse_query_is_not_a_response():
    assert parse_header(header(1, 0x0100))["is_response"] is False


def test_parse_response_flag():
    assert parse_header(header(1, 0x8180))["is_response"] is True


def test_parse_counts():
    h = parse_header(header(1, 0x8180, qd=1, an=3))
    assert h["questions"] == 1
    assert h["answers"] == 3


def test_accept_matching_response():
    pending = {(0x1234, "example.com")}
    r = (0x1234, "example.com", True, "93.184.216.34")
    assert accept_response(pending, r) == "93.184.216.34"


def test_reject_wrong_id():
    pending = {(0x1234, "example.com")}
    forged = (0x9999, "example.com", True, "6.6.6.6")
    assert accept_response(pending, forged) is None


def test_reject_name_never_queried():
    pending = {(0x1234, "example.com")}
    forged = (0x1234, "evil.com", True, "6.6.6.6")
    assert accept_response(pending, forged) is None


def test_reject_a_query_posing_as_an_answer():
    pending = {(0x1234, "example.com")}
    not_a_response = (0x1234, "example.com", False, "6.6.6.6")
    assert accept_response(pending, not_a_response) is None


def test_reject_when_nothing_pending():
    assert accept_response(set(), (0x1234, "example.com", True, "1.2.3.4")) is None
