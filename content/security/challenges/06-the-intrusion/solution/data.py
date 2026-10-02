AUTH_LOG = (
    [f"2026-02-01T09:00:{i:02d} sshd FAILED user=admin ip=203.0.113.9" for i in range(8)]
    + ["2026-02-01T09:00:30 sshd OK user=admin ip=203.0.113.9",
       "2026-02-01T09:42:00 sshd OK user=admin ip=203.0.113.9"]
)
INDICATORS = ["port_scan", "credential_compromise", "data_exfiltration"]
