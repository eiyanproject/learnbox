def parse_line(line):
    # Robust by design: a line that does not fit the shape returns None rather
    # than raising, because real logs are full of surprises.
    parts = line.split()
    if len(parts) < 3:
        return None
    rec = {"ts": parts[0], "service": parts[1], "result": parts[2],
           "user": None, "ip": None}
    for p in parts[3:]:
        if p.startswith("user="):
            rec["user"] = p[5:]
        elif p.startswith("ip="):
            rec["ip"] = p[3:]
    if rec["result"] not in ("FAILED", "OK"):
        return None
    return rec


def failed_by_ip(lines):
    counts = {}
    for line in lines:
        rec = parse_line(line)
        if rec and rec["result"] == "FAILED" and rec["ip"]:
            counts[rec["ip"]] = counts.get(rec["ip"], 0) + 1
    return counts


def compromised_ips(lines, threshold=5):
    # The story the logs tell: a flood of failures from an ip, then an OK from
    # the same ip. That success is a guess that finally worked.
    failures = {}
    compromised = set()
    for line in lines:
        rec = parse_line(line)
        if not rec or not rec["ip"]:
            continue
        if rec["result"] == "FAILED":
            failures[rec["ip"]] = failures.get(rec["ip"], 0) + 1
        elif rec["result"] == "OK" and failures.get(rec["ip"], 0) > threshold:
            compromised.add(rec["ip"])
    return compromised


if __name__ == "__main__":
    log = [f"2026-01-02T03:04:{i:02d} sshd FAILED user=admin ip=10.0.0.9"
           for i in range(8)]
    log.append("2026-01-02T03:05:00 sshd OK user=admin ip=10.0.0.9")
    print("failed:", failed_by_ip(log))
    print("compromised:", compromised_ips(log))
