from verdict import investigate
from data import AUTH_LOG, INDICATORS


def test_identifies_compromised_ip():
    assert investigate(AUTH_LOG, INDICATORS)["compromised_ip"] == "203.0.113.9"


def test_classifies_worst_severity():
    assert investigate(AUTH_LOG, INDICATORS)["severity"] == "critical"


def test_containment_matches_severity():
    assert investigate(AUTH_LOG, INDICATORS)["containment"] == "isolate the host"


def test_dwell_time_first_to_last():
    # 09:00:00 to 09:42:00 is 42 minutes.
    assert investigate(AUTH_LOG, INDICATORS)["dwell_seconds"] == 42 * 60


def test_lower_severity_without_critical_indicator():
    v = investigate(AUTH_LOG, ["port_scan", "credential_compromise"])
    assert v["severity"] == "high"
    assert v["containment"] == "disable the affected account"


def test_no_compromise_without_bruteforce():
    clean = ["2026-02-01T09:00:00 sshd OK user=admin ip=10.0.0.5"]
    assert investigate(clean, ["port_scan"])["compromised_ip"] is None


def test_verdict_has_all_fields():
    v = investigate(AUTH_LOG, INDICATORS)
    assert set(v) == {"compromised_ip", "severity", "containment", "dwell_seconds"}
