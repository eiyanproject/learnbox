RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def dedupe(alerts):
    pass


def by_severity(alerts):
    pass


def most_urgent(alerts):
    pass


if __name__ == "__main__":
    alerts = [
        {"source": "10.0.0.9", "kind": "failed-login", "severity": "low"},
        {"source": "10.0.0.9", "kind": "failed-login", "severity": "low"},
        {"source": "db01", "kind": "data-exfil", "severity": "critical"},
    ]
    print("deduped:", dedupe(alerts))
    print("most urgent:", most_urgent(alerts))
