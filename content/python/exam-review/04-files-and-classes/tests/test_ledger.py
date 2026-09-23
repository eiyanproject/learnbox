import pytest

from ledger import Ledger


def test_new_ledger_is_empty():
    assert Ledger().total() == 0


def test_each_ledger_has_its_own_entries():
    a, b = Ledger(), Ledger()
    a.add("ana", 10)
    assert b.total() == 0


def test_total_sums_every_entry():
    ledger = Ledger()
    ledger.add("ana", 10)
    ledger.add("budi", 5.5)
    assert ledger.total() == 15.5


def test_top_spender_of_an_empty_ledger():
    assert Ledger().top_spender() is None


def test_top_spender_adds_up_repeat_entries():
    ledger = Ledger()
    ledger.add("ana", 5)
    ledger.add("budi", 8)
    ledger.add("ana", 6)
    assert ledger.top_spender() == "ana"


def test_top_spender_breaks_ties_alphabetically():
    ledger = Ledger()
    ledger.add("zoe", 10)
    ledger.add("amy", 10)
    assert ledger.top_spender() == "amy"


def test_save_writes_one_line_per_entry(tmp_path):
    p = tmp_path / "ledger.csv"
    ledger = Ledger()
    ledger.add("ana", 10)
    ledger.add("budi", 5.5)
    ledger.save(p)
    assert p.read_text(encoding="utf-8").splitlines() == ["ana,10", "budi,5.5"]


def test_round_trip(tmp_path):
    p = tmp_path / "ledger.csv"
    original = Ledger()
    original.add("ana", 10)
    original.add("budi", 5.5)
    original.save(p)

    restored = Ledger.load(p)
    assert restored.total() == original.total()
    assert restored.top_spender() == original.top_spender()


def test_load_returns_a_ledger(tmp_path):
    p = tmp_path / "ledger.csv"
    Ledger().save(p)
    assert isinstance(Ledger.load(p), Ledger)


def test_load_of_an_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    assert Ledger.load(p).total() == 0


def test_save_truncates_an_existing_file(tmp_path):
    p = tmp_path / "ledger.csv"
    first = Ledger()
    first.add("ana", 10)
    first.save(p)

    second = Ledger()
    second.add("budi", 1)
    second.save(p)
    assert Ledger.load(p).total() == 1
