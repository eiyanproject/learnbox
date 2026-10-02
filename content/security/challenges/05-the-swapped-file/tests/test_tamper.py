from tamper import find_tampered, extract_payload
from data import ORIGINAL, CURRENT


def test_finds_the_swapped_file():
    assert find_tampered(ORIGINAL, CURRENT) == "logo.png"


def test_none_when_nothing_changed():
    assert find_tampered(ORIGINAL, ORIGINAL) is None


def test_extracts_the_hidden_payload():
    name = find_tampered(ORIGINAL, CURRENT)
    assert extract_payload(CURRENT[name]) == b"flag{hidden_after_the_image_ends}"


def test_clean_file_has_no_payload():
    assert extract_payload(ORIGINAL["logo.png"]) == b""
