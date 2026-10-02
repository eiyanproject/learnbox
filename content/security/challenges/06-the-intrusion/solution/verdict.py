from datetime import datetime
from data import AUTH_LOG, INDICATORS

SEVERITY = {"data_exfiltration": "critical", "ransomware": "critical",
            "credential_compromise": "high", "malware": "high",
            "port_scan": "low", "failed_logins": "low"}
RANK = {"critical": 3, "high": 2, "low": 0, "none": -1}
CONTAINMENT = {"critical": "isolate the host", "high": "disable the affected account",
               "low": "monitor", "none": "monitor"}


def _parse(line):
    parts = line.split()
    rec = {"ts": parts[0], "result": parts[2], "ip": None}
    for p in parts[3:]:
        if p.startswith("ip="):
            rec["ip"] = p[3:]
    return rec


def investigate(auth_log, indicators):
    # Who got in: a flood of failures from an ip, then a success.
    failures, compromised = {}, None
    for line in auth_log:
        rec = _parse(line)
        if rec["result"] == "FAILED":
            failures[rec["ip"]] = failures.get(rec["ip"], 0) + 1
        elif rec["result"] == "OK" and failures.get(rec["ip"], 0) > 5:
            compromised = rec["ip"]

    # How bad: the worst indicator present.
    severity = "none"
    for ind in indicators:
        level = SEVERITY.get(ind, "none")
        if RANK[level] > RANK[severity]:
            severity = level

    # How long: first to last auth-log timestamp.
    times = [datetime.fromisoformat(_parse(l)["ts"]) for l in auth_log]
    dwell = int((max(times) - min(times)).total_seconds()) if times else 0

    return {"compromised_ip": compromised, "severity": severity,
            "containment": CONTAINMENT[severity], "dwell_seconds": dwell}


if __name__ == "__main__":
    print(investigate(AUTH_LOG, INDICATORS))
