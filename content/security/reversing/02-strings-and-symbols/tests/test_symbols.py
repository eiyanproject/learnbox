from symbols import extract_strings, find_symbol, imported_danger


def test_extract_strings_basic():
    assert extract_strings(b"\x00/etc/passwd\x00") == ["/etc/passwd"]


def test_extract_strings_min_len():
    assert extract_strings(b"\x00ok\x00longer\x00") == ["longer"]


def test_extract_strings_finds_a_url():
    data = b"\x01\x02http://evil.example/c2\x00rest"
    assert "http://evil.example/c2" in extract_strings(data)


def test_find_symbol_hit():
    syms = [("main", 0x401050), ("gets", 0x401030)]
    assert find_symbol(syms, "gets") == 0x401030


def test_find_symbol_miss():
    assert find_symbol([("main", 1)], "system") is None


def test_imported_danger_flags_risky():
    syms = [("main", 1), ("gets", 2), ("printf", 3), ("system", 4)]
    assert imported_danger(syms) == {"gets", "system"}


def test_imported_danger_none():
    syms = [("main", 1), ("printf", 2), ("malloc", 3)]
    assert imported_danger(syms) == set()


def test_imported_danger_finds_strcpy():
    assert "strcpy" in imported_danger([("strcpy", 0x1000)])
