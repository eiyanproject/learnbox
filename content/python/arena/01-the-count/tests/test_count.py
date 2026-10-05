from count import winner


def test_clear_winner():
    assert winner(["ana", "bo", "ana"]) == "Ana"


def test_tie_goes_to_the_alphabet():
    assert winner(["bo", "ana"]) == "Ana"
    assert winner(["cy", "bo", "cy", "bo", "ana"]) == "Bo"


def test_votes_count_however_they_were_typed():
    assert winner([" BO ", "bo", "Ana"]) == "Bo"
    assert winner(["ANA", "ana ", " Ana", "bo", "bo"]) == "Ana"


def test_no_votes():
    assert winner([]) is None


def test_single_vote():
    assert winner(["zed"]) == "Zed"


def test_the_list_is_left_alone():
    votes = [" ana", "BO"]
    winner(votes)
    assert votes == [" ana", "BO"]


def test_a_big_count():
    votes = ["ana"] * 400 + ["bo"] * 401 + ["cy"] * 399
    assert winner(votes) == "Bo"
