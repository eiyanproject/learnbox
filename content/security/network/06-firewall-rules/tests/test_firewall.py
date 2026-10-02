from firewall import matches, evaluate

SSH = {"action": "allow", "proto": "tcp", "src": "10.0.0.5", "dst_port": 22}
HTTPS = {"action": "allow", "proto": "tcp", "dst_port": 443}


def test_matches_exact():
    assert matches(SSH, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22})


def test_matches_wildcard_field():
    # HTTPS rule leaves src unspecified, so any source matches.
    assert matches(HTTPS, {"proto": "tcp", "src": "1.2.3.4", "dst_port": 443})


def test_does_not_match_wrong_port():
    assert not matches(SSH, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 23})


def test_does_not_match_wrong_src():
    assert not matches(SSH, {"proto": "tcp", "src": "9.9.9.9", "dst_port": 22})


def test_evaluate_allows_matching_traffic():
    rules = [SSH, HTTPS]
    assert evaluate(rules, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22}) == "allow"
    assert evaluate(rules, {"proto": "tcp", "src": "8.8.8.8", "dst_port": 443}) == "allow"


def test_default_deny_for_unmatched():
    rules = [SSH, HTTPS]
    assert evaluate(rules, {"proto": "tcp", "src": "1.2.3.4", "dst_port": 22}) == "deny"


def test_default_deny_when_no_rules():
    assert evaluate([], {"proto": "tcp", "src": "x", "dst_port": 80}) == "deny"


def test_first_match_wins():
    # A deny placed first shadows the allow below it.
    rules = [
        {"action": "deny", "dst_port": 22},
        {"action": "allow", "proto": "tcp", "src": "10.0.0.5", "dst_port": 22},
    ]
    assert evaluate(rules, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22}) == "deny"


def test_order_changes_the_outcome():
    # Swap them and the specific allow now wins for that source.
    rules = [
        {"action": "allow", "proto": "tcp", "src": "10.0.0.5", "dst_port": 22},
        {"action": "deny", "dst_port": 22},
    ]
    assert evaluate(rules, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22}) == "allow"
    assert evaluate(rules, {"proto": "tcp", "src": "9.9.9.9", "dst_port": 22}) == "deny"
