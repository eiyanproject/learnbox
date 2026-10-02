from sniff import find_exfil
from data import EXFIL


def test_recovers_the_secret():
    assert find_exfil(EXFIL) == "flag{data_left_on_the_wire}"


def test_returns_a_string():
    assert isinstance(find_exfil(EXFIL), str)


def test_none_when_no_exfil():
    # A pcap with no POST body has nothing to find.
    import struct
    empty = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    assert find_exfil(empty) is None
