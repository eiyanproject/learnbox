from datetime import datetime
from data import AUTH_LOG, INDICATORS

SEVERITY = {"data_exfiltration": "critical", "ransomware": "critical",
            "credential_compromise": "high", "malware": "high",
            "port_scan": "low", "failed_logins": "low"}
RANK = {"critical": 3, "high": 2, "low": 0, "none": -1}
CONTAINMENT = {"critical": "isolate the host", "high": "disable the affected account",
               "low": "monitor", "none": "monitor"}


def investigate(auth_log, indicators):
    pass


if __name__ == "__main__":
    print(investigate(AUTH_LOG, INDICATORS))
