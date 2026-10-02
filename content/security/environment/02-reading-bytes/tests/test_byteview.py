from byteview import hexdump, find_strings


def test_hexdump_offset_and_bytes():
    out = hexdump(b"\x7fELF")
    assert out.startswith("00000000: 7f 45 4c 46")


def test_hexdump_ascii_column():
    out = hexdump(b"\x7fELF")
    assert out.endswith(".ELF")


def test_hexdump_unprintable_becomes_dot():
    assert hexdump(b"\x00\xff") == "00000000: 00 ff  .."


def test_hexdump_wraps_every_16_bytes():
    out = hexdump(bytes(range(20)))
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[1].startswith("00000010: 10 11 12 13")


def test_hexdump_empty():
    assert hexdump(b"") == ""


def test_find_strings_basic():
    assert find_strings(b"\x00password\x00") == ["password"]


def test_find_strings_respects_min_len():
    # "ok" is too short at the default length of 4; "longer" survives.
    assert find_strings(b"\x00ok\x00longer\x00") == ["longer"]


def test_find_strings_custom_min_len():
    assert find_strings(b"\x00ok\x00", min_len=2) == ["ok"]


def test_find_strings_multiple_runs_in_order():
    assert find_strings(b"first\x00\x01\x02second") == ["first", "second"]


def test_find_strings_run_at_the_very_end():
    assert find_strings(b"\xfftrailing") == ["trailing"]


def test_find_strings_none_when_all_binary():
    assert find_strings(b"\x00\x01\x02\x03") == []


def test_find_strings_returns_str_not_bytes():
    out = find_strings(b"hello world")
    assert all(isinstance(s, str) for s in out)
