import pytest

from rules import describe_failure, is_valid_username, normalise


def test_normalise_trims_and_lowercases():
    assert normalise("  Ada  ") == "ada"
    assert normalise("ADA_99") == "ada_99"


def test_normalise_leaves_a_clean_name_alone():
    assert normalise("ada_lovelace") == "ada_lovelace"


@pytest.mark.parametrize("name", ["ada", "ada_lovelace_99", "a1b", "abc", "a_b"])
def test_accepts_valid_names(name):
    assert is_valid_username(name), f"{name!r} should be valid"


@pytest.mark.parametrize(
    "name, reason",
    [
        ("ad", "too short"),
        ("", "too short"),
        ("a" * 17, "too long"),
        ("ada lovelace", "invalid characters"),
        ("ada!", "invalid characters"),
        ("9ada", "must start with a letter"),
        ("_ada", "must start with a letter"),
        ("ada_", "must not end with an underscore"),
        ("ada", "ok"),
    ],
)
def test_describes_the_first_broken_rule(name, reason):
    assert describe_failure(name) == reason


def test_boundaries_are_inclusive():
    assert is_valid_username("abc"), "3 characters is the minimum, and allowed"
    assert is_valid_username("a" * 16), "16 characters is the maximum, and allowed"
    assert not is_valid_username("ab")
    assert not is_valid_username("a" * 17)


def test_uppercase_is_normalised_not_rejected():
    """The specification was silent; normalising is the decision taken."""
    assert is_valid_username("Ada")


def test_surrounding_whitespace_is_trimmed_not_rejected():
    assert is_valid_username("  ada  ")


def test_length_is_measured_after_normalising():
    assert not is_valid_username("  ad  "), "trimmed to 2 characters, so too short"
