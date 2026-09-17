from patterns import find_hashtags, is_valid_username, mask_emails, normalize_phone, parse_log_line


def test_hashtags():
    assert find_hashtags("#python and #re_2, not a#b? #3d") == ["python", "re_2", "b", "3d"]
    assert find_hashtags("no tags") == []


def test_parse_log_line():
    assert parse_log_line("2026-09-18 ERROR disk full") == {
        "date": "2026-09-18",
        "level": "ERROR",
        "message": "disk full",
    }
    assert parse_log_line("2026-01-02 INFO started worker 3\n")["message"] == "started worker 3"


def test_parse_log_line_rejects():
    assert parse_log_line("18-09-2026 ERROR x") is None
    assert parse_log_line("2026-09-18 error lowercase level") is None
    assert parse_log_line("2026-09-18 WARN") is None
    assert parse_log_line("") is None


def test_valid_usernames():
    for ok in ["ana", "budi_99", "a" * 16, "x_1"]:
        assert is_valid_username(ok), ok


def test_invalid_usernames():
    for bad in ["an", "a" * 17, "9lives", "Ana", "ana-b", "ana b", "_ana", "ana\n"]:
        assert not is_valid_username(bad), bad


def test_normalize_phone():
    assert normalize_phone("0812-3456 789") == "628123456789"
    assert normalize_phone("+62 812 3456 789") == "628123456789"
    assert normalize_phone("(021) 555 0100") == "62215550100"


def test_normalize_phone_only_leading_zero():
    assert normalize_phone("8100") == "8100"


def test_mask_emails():
    assert mask_emails("mail ana.b@x.io now") == "mail ***@x.io now"
    assert mask_emails("a@b.com, c+d@mail.co.id") == "***@b.com, ***@mail.co.id"
    assert mask_emails("no email @ here") == "no email @ here"
