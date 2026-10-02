from incident import severity, containment, next_phase, is_valid_order


def test_severity_takes_the_worst():
    inc = ["port_scan", "credential_compromise", "data_exfiltration"]
    assert severity(inc) == "critical"


def test_severity_high():
    assert severity(["failed_logins", "credential_compromise"]) == "high"


def test_severity_low():
    assert severity(["port_scan", "failed_logins"]) == "low"


def test_severity_none_when_empty():
    assert severity([]) == "none"


def test_severity_ignores_unknown_indicators():
    assert severity(["something_new", "port_scan"]) == "low"


def test_containment_critical_isolates():
    assert containment("critical") == "isolate the host"


def test_containment_high_disables_account():
    assert containment("high") == "disable the affected account"


def test_containment_low_monitors():
    assert containment("low") == "monitor"


def test_next_phase():
    assert next_phase("identify") == "contain"
    assert next_phase("contain") == "eradicate"


def test_next_phase_after_last_is_none():
    assert next_phase("lessons") is None


def test_valid_order_accepts_canonical():
    assert is_valid_order(["identify", "contain", "eradicate", "recover", "lessons"])


def test_valid_order_accepts_a_subset_in_order():
    assert is_valid_order(["identify", "contain", "recover"])


def test_invalid_order_recover_before_eradicate():
    # Recovering before eradicating reinfects the restored system.
    assert not is_valid_order(["identify", "recover", "eradicate"])


def test_invalid_order_eradicate_before_contain():
    assert not is_valid_order(["eradicate", "contain"])
