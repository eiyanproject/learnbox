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
    pass


def containment(sev):
    pass


def next_phase(current):
    pass


def is_valid_order(phases):
    pass


if __name__ == "__main__":
    inc = ["port_scan", "credential_compromise", "data_exfiltration"]
    sev = severity(inc)
    print("severity:", sev, "-> contain by:", containment(sev))
    print("valid order?", is_valid_order(["identify", "contain", "recover"]))
