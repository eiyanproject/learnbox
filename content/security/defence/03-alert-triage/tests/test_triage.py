from triage import dedupe, by_severity, most_urgent


def alert(source, kind, severity):
    return {"source": source, "kind": kind, "severity": severity}


ALERTS = [
    alert("10.0.0.9", "failed-login", "low"),
    alert("10.0.0.9", "failed-login", "low"),
    alert("10.0.0.9", "failed-login", "low"),
    alert("db01", "data-exfil", "critical"),
    alert("web01", "sqli-attempt", "high"),
]


def test_dedupe_counts_duplicates():
    assert dedupe(ALERTS)[("10.0.0.9", "failed-login")] == 3


def test_dedupe_keeps_distinct_separate():
    out = dedupe(ALERTS)
    assert out[("db01", "data-exfil")] == 1
    assert out[("web01", "sqli-attempt")] == 1


def test_dedupe_shrinks_the_queue():
    # Five alerts collapse to three distinct facts.
    assert len(dedupe(ALERTS)) == 3


def test_by_severity_orders_critical_first():
    ordered = by_severity(ALERTS)
    assert ordered[0]["severity"] == "critical"
    assert ordered[1]["severity"] == "high"


def test_by_severity_is_stable_among_equals():
    a = [alert("a", "x", "low"), alert("b", "y", "low")]
    assert [x["source"] for x in by_severity(a)] == ["a", "b"]


def test_most_urgent():
    assert most_urgent(ALERTS)["kind"] == "data-exfil"


def test_most_urgent_empty():
    assert most_urgent([]) is None


def test_most_urgent_single():
    one = [alert("x", "y", "medium")]
    assert most_urgent(one)["severity"] == "medium"
