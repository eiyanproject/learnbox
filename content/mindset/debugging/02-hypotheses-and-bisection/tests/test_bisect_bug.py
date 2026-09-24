import pytest

from bisect_bug import load, parse_row, summarise

HEADER = ["name", "quantity", "price"]
ROWS = [HEADER, ["apple", "2", "1.5"], ["pear", "1", "2.0"]]


def test_parse_row_converts_the_types():
    assert parse_row(["apple", "2", "1.5"]) == ("apple", 2, 1.5)


def test_parse_row_returns_numbers_not_strings():
    _, quantity, price = parse_row(["apple", "2", "1.5"])
    assert isinstance(quantity, int), "quantity should be an int"
    assert isinstance(price, float), "price should be a float"


def test_parse_row_rejects_a_short_row():
    with pytest.raises(ValueError):
        parse_row(["apple", "2"])


def test_parse_row_rejects_a_non_numeric_quantity():
    with pytest.raises(ValueError):
        parse_row(["apple", "many", "1.5"])


def test_load_skips_the_header():
    assert len(load(ROWS)) == 2


def test_load_ignores_unparseable_rows():
    rows = [HEADER, ["apple", "2", "1.5"], ["broken"], ["pear", "x", "2.0"]]
    assert len(load(rows)) == 1, "one good row survives, the other two are dropped"


def test_load_of_only_a_header():
    assert load([HEADER]) == []


def test_summarise_counts_items():
    assert summarise(ROWS)["items"] == 2


def test_summarise_totals_correctly():
    assert summarise(ROWS)["total"] == 5.0


def test_summarise_of_an_empty_file():
    assert summarise([HEADER]) == {"items": 0, "total": 0}


def test_summarise_survives_bad_rows():
    rows = [HEADER, ["apple", "2", "1.5"], ["junk", "junk", "junk"]]
    assert summarise(rows) == {"items": 1, "total": 3.0}
