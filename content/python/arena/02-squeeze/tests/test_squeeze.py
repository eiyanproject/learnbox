from squeeze import squeeze, unsqueeze


def test_squeeze_runs():
    assert squeeze("aaabccdddd") == "a3bc2d4"


def test_squeeze_leaves_singles_alone():
    assert squeeze("abc") == "abc"


def test_squeeze_empty():
    assert squeeze("") == ""


def test_squeeze_is_case_sensitive():
    assert squeeze("aAAa") == "aA2a"


def test_squeeze_long_run():
    assert squeeze("x" * 12) == "x12"


def test_squeeze_the_same_letter_twice():
    assert squeeze("aabaa") == "a2ba2"


def test_unsqueeze_runs():
    assert unsqueeze("a3bc2d4") == "aaabccdddd"


def test_unsqueeze_multi_digit_counts():
    assert unsqueeze("x12") == "x" * 12
    assert unsqueeze("a100b") == "a" * 100 + "b"


def test_unsqueeze_empty():
    assert unsqueeze("") == ""


def test_round_trip():
    for text in ["", "a", "zzzzzzzzzzzzzzzzzzzzzzz", "abcabc", "aabbbccccd", "Mississippi"]:
        assert unsqueeze(squeeze(text)) == text
