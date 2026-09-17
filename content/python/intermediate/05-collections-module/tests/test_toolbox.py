from toolbox import grade_for, index_by_tag, k_smallest, moving_average, top_words


def test_top_words():
    text = "the cat and The dog and THE bird"
    assert top_words(text, 2) == [("the", 3), ("and", 2)]
    assert top_words("", 3) == []


def test_index_by_tag():
    items = [("ana", ["red", "admin"]), ("budi", ["blue"]), ("citra", ["red"])]
    result = index_by_tag(items)
    assert result == {"red": ["ana", "citra"], "admin": ["ana"], "blue": ["budi"]}
    assert type(result) is dict, "return a plain dict"
    assert "missing" not in result


def test_moving_average():
    assert list(moving_average([1, 2, 3, 4, 5], 2)) == [1.5, 2.5, 3.5, 4.5]
    assert list(moving_average([10, 20, 30], 3)) == [20.0]
    assert list(moving_average([1, 2], 3)) == []


def test_moving_average_is_lazy():
    def forever():
        n = 0
        while True:
            n += 1
            yield n

    avg = moving_average(forever(), 3)
    assert next(avg) == 2.0
    assert next(avg) == 3.0


def test_k_smallest():
    assert k_smallest([5, 1, 9, 3, 7], 3) == [1, 3, 5]
    assert k_smallest([2], 5) == [2]


def test_grades():
    assert [grade_for(s) for s in (0, 59, 60, 69, 70, 79, 80, 89, 90, 100)] == list("FFDDCCBBAA")
