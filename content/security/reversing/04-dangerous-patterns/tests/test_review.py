from review import dangerous_calls, safer_alternative, review


def test_dangerous_calls_found():
    out = dangerous_calls(["printf", "gets", "malloc"])
    assert "gets" in out
    assert "printf" not in out


def test_dangerous_calls_gives_reasons():
    assert "overflow" in dangerous_calls(["gets"])["gets"]


def test_dangerous_calls_none():
    assert dangerous_calls(["printf", "malloc", "free"]) == {}


def test_dangerous_calls_multiple():
    out = dangerous_calls(["strcpy", "system", "puts"])
    assert set(out.keys()) == {"strcpy", "system"}


def test_safer_alternative_known():
    assert safer_alternative("gets") == "fgets"
    # strncpy is the trap: it can leave the buffer unterminated.
    assert safer_alternative("strcpy") == "snprintf"
    assert safer_alternative("strcpy") != "strncpy"
    assert safer_alternative("sprintf") == "snprintf"


def test_safer_alternative_unknown():
    assert safer_alternative("printf") is None


def test_review_flags_risky_functions():
    code = {
        "read_name": ["printf", "gets"],
        "copy_field": ["strcpy"],
        "greet": ["printf", "puts"],
    }
    assert review(code) == {"read_name", "copy_field"}


def test_review_clean_code():
    code = {"add": ["malloc"], "show": ["printf"]}
    assert review(code) == set()
