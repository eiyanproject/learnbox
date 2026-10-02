from logs import parse_line, failed_by_ip, compromised_ips


def many_fails(ip, n):
    return [f"2026-01-02T03:04:{i:02d} sshd FAILED user=admin ip={ip}" for i in range(n)]


def test_parse_a_failed_line():
    r = parse_line("2026-01-02T03:04:05 sshd FAILED user=admin ip=10.0.0.9")
    assert r["result"] == "FAILED"
    assert r["user"] == "admin"
    assert r["ip"] == "10.0.0.9"


def test_parse_an_ok_line():
    assert parse_line("2026-01-02T03:04:05 sshd OK user=root ip=1.2.3.4")["result"] == "OK"


def test_parse_junk_returns_none():
    assert parse_line("") is None
    assert parse_line("garbage") is None


def test_parse_unknown_result_is_none():
    assert parse_line("2026-01-02T03:04:05 sshd MAYBE user=x ip=1.1.1.1") is None


def test_failed_by_ip_counts():
    counts = failed_by_ip(many_fails("10.0.0.9", 4) + many_fails("1.1.1.1", 2))
    assert counts == {"10.0.0.9": 4, "1.1.1.1": 2}


def test_failed_by_ip_ignores_success():
    lines = many_fails("9.9.9.9", 3) + ["2026-01-02T03:05:00 sshd OK user=a ip=9.9.9.9"]
    assert failed_by_ip(lines)["9.9.9.9"] == 3


def test_compromise_detected():
    lines = many_fails("10.0.0.9", 8) + ["2026-01-02T03:05:00 sshd OK user=admin ip=10.0.0.9"]
    assert compromised_ips(lines) == {"10.0.0.9"}


def test_no_compromise_without_success():
    assert compromised_ips(many_fails("10.0.0.9", 20)) == set()


def test_no_compromise_below_threshold():
    lines = many_fails("10.0.0.9", 2) + ["2026-01-02T03:05:00 sshd OK user=admin ip=10.0.0.9"]
    assert compromised_ips(lines) == set()


def test_legitimate_login_is_not_a_compromise():
    # A success with no preceding flood is normal.
    assert compromised_ips(["2026-01-02T03:04:05 sshd OK user=admin ip=10.0.0.5"]) == set()
