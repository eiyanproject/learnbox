import pytest

from billing import bill, discount, line_total, parse_line, subtotal

ORDER = ["2 x coffee @ 3.50", "1 x cake @ 4", "what?"]


# ---- what bill() already did must still be true


def test_bill_as_it_always_was():
    result = bill(ORDER)
    assert result["items"] == 2
    assert result["skipped"] == 1
    assert result["subtotal"] == 11.0
    assert result["total"] == 11.0


def test_bill_of_nothing():
    assert bill([]) == {"items": 0, "skipped": 0, "subtotal": 0.0, "discount": 0.0, "total": 0.0}


@pytest.mark.parametrize(
    "line",
    [
        "what?",
        "2 x coffee",
        "2 x coffee @ 3 @ 4",
        "coffee @ 3.50",
        "two x coffee @ 3.50",
        "2 x coffee @ cheap",
        "0 x coffee @ 3.50",
        "-1 x coffee @ 3.50",
        "2 x coffee @ -1",
        "2 x  @ 3.50",
        "2.5 x coffee @ 3.50",
        "",
    ],
)
def test_bill_skips_what_it_always_skipped(line):
    result = bill([line, "1 x tea @ 2"])
    assert (result["items"], result["skipped"], result["total"]) == (1, 1, 2.0)


def test_bill_tolerates_spacing():
    assert bill(["  3 x  green tea  @  1.5  "])["subtotal"] == 4.5


def test_bill_rounds_the_money():
    assert bill(["3 x sweet @ 0.1"])["subtotal"] == 0.3


# ---- the pieces


def test_parse_line():
    assert parse_line("2 x coffee @ 3.50") == {"qty": 2, "name": "coffee", "price": 3.5}
    assert parse_line("  3 x  green tea  @  1.5  ") == {"qty": 3, "name": "green tea", "price": 1.5}


@pytest.mark.parametrize("line", ["what?", "0 x coffee @ 3.50", "2 x coffee @ -1", "2 x  @ 3.50", "x @ 1"])
def test_parse_line_refuses_what_bill_skips(line):
    with pytest.raises(ValueError):
        parse_line(line)


def test_line_total():
    assert line_total({"qty": 2, "name": "coffee", "price": 3.5}) == 7.0


def test_subtotal():
    items = [{"qty": 2, "name": "coffee", "price": 3.5}, {"qty": 1, "name": "cake", "price": 4.0}]
    assert subtotal(items) == 11.0
    assert subtotal([]) == 0.0
    assert subtotal([{"qty": 3, "name": "sweet", "price": 0.1}]) == 0.3


def test_discount_codes():
    assert discount(11.0, None) == 0.0
    assert discount(11.0, "TEN") == 1.1
    assert discount(11.0, "FIVER") == 5.0
    assert discount(33.33, "TEN") == 3.33


def test_fiver_never_takes_more_than_there_is():
    assert discount(3.2, "FIVER") == 3.2
    assert discount(0.0, "FIVER") == 0.0


def test_unknown_code():
    with pytest.raises(ValueError):
        discount(11.0, "FREE")
    with pytest.raises(ValueError):
        discount(11.0, "ten")


# ---- the new feature


def test_bill_with_ten():
    assert bill(ORDER, "TEN") == {"items": 2, "skipped": 1, "subtotal": 11.0, "discount": 1.1, "total": 9.9}


def test_bill_with_fiver():
    assert bill(ORDER, "FIVER")["total"] == 6.0
    assert bill(["1 x tea @ 2"], "FIVER") == {"items": 1, "skipped": 0, "subtotal": 2.0, "discount": 2.0, "total": 0.0}


def test_bill_without_a_code_reports_no_discount():
    assert bill(ORDER)["discount"] == 0.0
    assert bill(ORDER, code=None)["total"] == 11.0


def test_bill_with_an_unknown_code():
    with pytest.raises(ValueError):
        bill(ORDER, "FREE")
