from detect import matches, alerts, threshold_alert

ROOT_LOGIN = {"name": "root login", "when": {"user": "root", "result": "OK"}}
BRUTE = {"name": "brute force", "when": {"result": "FAILED"}, "count": 5}


def test_matches_all_fields():
    assert matches(ROOT_LOGIN, {"user": "root", "result": "OK", "ip": "1.1.1.1"})


def test_matches_fails_on_one_field():
    assert not matches(ROOT_LOGIN, {"user": "root", "result": "FAILED"})


def test_matches_ignores_unmentioned_fields():
    # The rule says nothing about ip, so any ip is fine.
    assert matches(ROOT_LOGIN, {"user": "root", "result": "OK", "ip": "9.9.9.9"})


def test_matches_missing_field():
    assert not matches(ROOT_LOGIN, {"user": "root"})


def test_alerts_finds_matches():
    events = [
        {"user": "root", "result": "OK"},
        {"user": "alice", "result": "OK"},
        {"user": "root", "result": "OK"},
    ]
    out = alerts([ROOT_LOGIN], events)
    assert len(out) == 2
    assert all(name == "root login" for name, _ in out)


def test_alerts_no_match():
    assert alerts([ROOT_LOGIN], [{"user": "bob", "result": "OK"}]) == []


def test_threshold_fires_on_burst():
    assert threshold_alert(BRUTE, [{"result": "FAILED"}] * 8)


def test_threshold_quiet_below_limit():
    assert not threshold_alert(BRUTE, [{"result": "FAILED"}] * 3)


def test_threshold_counts_only_matches():
    events = [{"result": "FAILED"}] * 3 + [{"result": "OK"}] * 20
    assert not threshold_alert(BRUTE, events)
