from report import average, longest_word, percent, running_total


def test_average():
    assert average([2, 4, 9]) == 5.0
    assert average([7]) == 7.0


def test_average_of_nothing():
    assert average([]) == 0.0


def test_longest_word():
    assert longest_word("a bird sang") == "bird"
    assert longest_word("") == ""


def test_longest_word_prefers_the_first():
    assert longest_word("one two six") == "one"
    assert longest_word("to be or") == "to"


def test_running_total():
    assert running_total([1, 2, 3]) == [1, 3, 6]
    assert running_total([5]) == [5]
    assert running_total([]) == []


def test_running_total_leaves_the_list_alone():
    values = [4, 4]
    running_total(values)
    assert values == [4, 4]


def test_percent():
    assert percent(1, 4) == 25.0
    assert percent(1, 3) == 33.3
    assert percent(5, 5) == 100.0


def test_percent_of_nothing():
    assert percent(3, 0) == 0.0
