RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def dedupe(alerts):
    # A hundred identical alerts are one fact with a count, not a hundred lines.
    counts = {}
    for a in alerts:
        key = (a["source"], a["kind"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def by_severity(alerts):
    # Stable sort, highest severity first: equal-severity alerts keep their
    # arrival order, which preserves the timeline within a priority band.
    return sorted(alerts, key=lambda a: RANK[a["severity"]], reverse=True)


def most_urgent(alerts):
    if not alerts:
        return None
    return by_severity(alerts)[0]


if __name__ == "__main__":
    alerts = [
        {"source": "10.0.0.9", "kind": "failed-login", "severity": "low"},
        {"source": "10.0.0.9", "kind": "failed-login", "severity": "low"},
        {"source": "db01", "kind": "data-exfil", "severity": "critical"},
    ]
    print("deduped:", dedupe(alerts))
    print("most urgent:", most_urgent(alerts))
