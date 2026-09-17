from lookup import common_friends, group_by_first_letter, invert, word_counts


def test_word_counts_simple():
    assert word_counts("a b a") == {"a": 2, "b": 1}


def test_word_counts_ignores_case_and_punctuation():
    assert word_counts("The cat. The hat!  the BAT?") == {"the": 3, "cat": 1, "hat": 1, "bat": 1}


def test_word_counts_empty():
    assert word_counts("") == {}


def test_invert():
    assert invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert({}) == {}


def test_group_by_first_letter():
    words = ["Apple", "banana", "avocado", "Blueberry", "cherry"]
    assert group_by_first_letter(words) == {
        "a": ["Apple", "avocado"],
        "b": ["banana", "Blueberry"],
        "c": ["cherry"],
    }


def test_common_friends():
    assert common_friends(["dewi", "ana", "budi"], ["budi", "eka", "ana"]) == ["ana", "budi"]


def test_common_friends_none_and_duplicates():
    assert common_friends(["a"], ["b"]) == []
    assert common_friends(["x", "x"], ["x"]) == ["x"]
