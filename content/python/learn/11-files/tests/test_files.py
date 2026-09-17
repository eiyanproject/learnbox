import json

from files import average_score, count_lines, update_settings, write_report


def test_count_lines_skips_blank(tmp_path):
    p = tmp_path / "notes.txt"
    p.write_text("one\n\ntwo\n   \nthree\n")
    assert count_lines(p) == 3


def test_count_lines_accepts_str_path(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("x\ny")
    assert count_lines(str(p)) == 2


def test_write_report_sorted(tmp_path):
    p = tmp_path / "report.txt"
    write_report(p, {"budi": 81, "ana": 92})
    assert p.read_text() == "ana: 92\nbudi: 81\n"


def test_write_report_overwrites(tmp_path):
    p = tmp_path / "report.txt"
    p.write_text("old contents\n")
    write_report(p, {"x": 1})
    assert p.read_text() == "x: 1\n"


def test_average_score(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text("name,score\nana,90\nbudi,75\ncitra,82\n")
    assert average_score(p) == 82.3


def test_average_score_empty(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text("name,score\n")
    assert average_score(p) == 0.0


def test_update_settings_new_file(tmp_path):
    p = tmp_path / "settings.json"
    assert update_settings(p, {"theme": "dark"}) == {"theme": "dark"}
    assert json.loads(p.read_text()) == {"theme": "dark"}


def test_update_settings_merges(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"theme": "light", "size": 14}))
    result = update_settings(p, {"theme": "dark"})
    assert result == {"theme": "dark", "size": 14}
    assert json.loads(p.read_text()) == {"theme": "dark", "size": 14}
