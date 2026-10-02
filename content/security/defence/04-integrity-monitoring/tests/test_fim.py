from fim import baseline, compare


def test_baseline_hashes_each_file():
    import hashlib
    b = baseline({"a": b"hello"})
    assert b["a"] == hashlib.sha256(b"hello").hexdigest()


def test_baseline_distinguishes_contents():
    b = baseline({"a": b"one", "b": b"two"})
    assert b["a"] != b["b"]


def test_compare_detects_change():
    base = baseline({"/bin/login": b"good"})
    now = baseline({"/bin/login": b"backdoored"})
    assert compare(base, now)["changed"] == ["/bin/login"]


def test_compare_detects_added():
    base = baseline({"a": b"x"})
    now = baseline({"a": b"x", "/tmp/shell": b"evil"})
    assert compare(base, now)["added"] == ["/tmp/shell"]


def test_compare_detects_removed():
    base = baseline({"a": b"x", "b": b"y"})
    now = baseline({"a": b"x"})
    assert compare(base, now)["removed"] == ["b"]


def test_compare_clean_system():
    files = {"a": b"x", "b": b"y"}
    base = baseline(files)
    now = baseline(files)
    assert compare(base, now) == {"changed": [], "added": [], "removed": []}


def test_compare_sorts_results():
    base = baseline({"z": b"1", "a": b"1"})
    now = baseline({"z": b"2", "a": b"2"})
    assert compare(base, now)["changed"] == ["a", "z"]


def test_compare_all_three_at_once():
    base = baseline({"keep": b"same", "edit": b"before", "gone": b"x"})
    now = baseline({"keep": b"same", "edit": b"after", "new": b"y"})
    out = compare(base, now)
    assert out == {"changed": ["edit"], "added": ["new"], "removed": ["gone"]}
