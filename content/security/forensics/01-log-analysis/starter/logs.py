def parse_line(line):
    pass


def failed_by_ip(lines):
    pass


def compromised_ips(lines, threshold=5):
    pass


if __name__ == "__main__":
    log = [f"2026-01-02T03:04:{i:02d} sshd FAILED user=admin ip=10.0.0.9"
           for i in range(8)]
    log.append("2026-01-02T03:05:00 sshd OK user=admin ip=10.0.0.9")
    print("failed:", failed_by_ip(log))
    print("compromised:", compromised_ips(log))
