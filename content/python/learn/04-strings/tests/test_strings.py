from strings import initials, is_palindrome, mask_card, slugify


def test_initials_two_words():
    assert initials("ada lovelace") == "AL"


def test_initials_three_words_and_extra_spaces():
    assert initials("  grace  brewster hopper ") == "GBH"


def test_palindrome_simple():
    assert is_palindrome("racecar") is True
    assert is_palindrome("python") is False


def test_palindrome_ignores_case_spaces_and_punctuation():
    assert is_palindrome("Never odd or even") is True
    assert is_palindrome("A man, a plan, a canal: Panama!") is True


def test_mask_card():
    assert mask_card("4111111111111111") == "************1111"
    assert mask_card("12345") == "*2345"


def test_mask_card_short():
    assert mask_card("1234") == "1234"


def test_slugify():
    assert slugify("  Hello World  From Python ") == "hello-world-from-python"
    assert slugify("Learnbox") == "learnbox"
