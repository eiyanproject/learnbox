from solve import crack
from data import BLOB


def test_recovers_the_flag():
    assert crack(BLOB) == "flag{peel_back_the_layers}"


def test_returns_a_string():
    assert isinstance(crack(BLOB), str)


def test_flag_shape():
    flag = crack(BLOB)
    assert flag.startswith("flag{") and flag.endswith("}")
