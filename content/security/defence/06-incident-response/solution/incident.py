SEVERITY = {
    "data_exfiltration": "critical", "ransomware": "critical",
    "credential_compromise": "high", "malware_found": "high",
    "port_scan": "low", "failed_logins": "low",
}
RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0, "none": -1}
CONTAINMENT = {
    "critical": "isolate the host",
    "high": "disable the affected account",
    "low": "monitor",
    "none": "monitor",
}
PHASES = ["identify", "contain", "eradicate", "recover", "lessons"]


def severity(indicators):
    # Classify by the worst thing present: the response must match the most
    # serious indicator, not the average of them.
    worst = "none"
    for ind in indicators:
        level = SEVERITY.get(ind, "none")
        if RANK[level] > RANK[worst]:
            worst = level
    return worst


def containment(sev):
    return CONTAINMENT.get(sev, "monitor")


def next_phase(current):
    i = PHASES.index(current)
    return PHASES[i + 1] if i + 1 < len(PHASES) else None


def is_valid_order(phases):
    # The given phases must appear in the same relative order as the canonical
    # sequence: contain before eradicate, eradicate before recover.
    indices = [PHASES.index(p) for p in phases]
    return indices == sorted(indices)


if __name__ == "__main__":
    inc = ["port_scan", "credential_compromise", "data_exfiltration"]
    sev = severity(inc)
    print("severity:", sev, "-> contain by:", containment(sev))
    print("valid order?", is_valid_order(["identify", "contain", "recover"]))
