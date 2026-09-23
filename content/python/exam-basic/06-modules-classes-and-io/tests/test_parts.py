import pytest

from parts import Rect, Shape, load_lines, render, save_lines


def test_shape_stores_its_name():
    assert Shape("blob").name == "blob"


def test_created_is_shared_by_every_instance():
    before = Shape.created
    Shape("a")
    Shape("b")
    assert Shape.created == before + 2


def test_created_is_a_class_attribute_not_a_per_instance_one():
    before = Shape.created
    shape = Shape("c")
    # Reading through the instance must find the class attribute.
    assert shape.created == Shape.created == before + 1


def test_base_area_is_not_implemented():
    with pytest.raises(NotImplementedError):
        Shape("blob").area()


def test_rect_calls_super_init():
    rect = Rect(3, 4)
    assert rect.name == "rect"


def test_rect_area():
    assert Rect(3, 4).area() == 12


def test_rect_counts_towards_created():
    before = Shape.created
    Rect(1, 1)
    assert Shape.created == before + 1


def test_rect_is_a_shape():
    assert isinstance(Rect(1, 1), Shape)


def test_save_and_load_round_trip(tmp_path):
    p = tmp_path / "lines.txt"
    save_lines(p, ["alpha", "beta", "gamma"])
    assert load_lines(p) == ["alpha", "beta", "gamma"]


def test_save_lines_writes_one_line_each(tmp_path):
    p = tmp_path / "lines.txt"
    save_lines(p, ["a", "b"])
    assert p.read_text(encoding="utf-8") == "a\nb\n"


def test_save_lines_truncates_an_existing_file(tmp_path):
    p = tmp_path / "lines.txt"
    save_lines(p, ["old", "content", "here"])
    save_lines(p, ["new"])
    assert load_lines(p) == ["new"]


def test_load_lines_on_empty_file(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("", encoding="utf-8")
    assert load_lines(p) == []


@pytest.mark.parametrize(
    "name, score, expected",
    [
        ("ana", 92.0, "ana         92.0"),
        ("budi", 8.25, "budi         8.2"),
        ("verylongname", 5.0, "verylongname   5.0"),
    ],
)
def test_render(name, score, expected):
    assert render(name, score) == expected
