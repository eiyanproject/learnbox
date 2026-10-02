from datetime import datetime


def merge(sources):
    # One story from many logs: flatten every source and order by time.
    events = [e for source in sources for e in source]
    return sorted(events, key=lambda e: e[0])


def sequence(sources):
    return [desc for _, _, desc in merge(sources)]


def dwell_time(sources):
    # First malicious event to last: how long the intruder operated unseen.
    events = merge(sources)
    if not events:
        return 0
    first = datetime.fromisoformat(events[0][0])
    last = datetime.fromisoformat(events[-1][0])
    return int((last - first).total_seconds())


if __name__ == "__main__":
    firewall = [("2026-01-02T03:00:00", "fw", "port scan from 10.0.0.9")]
    auth = [("2026-01-02T03:05:00", "sshd", "brute-force login succeeded")]
    fileserver = [("2026-01-02T03:20:00", "nfs", "bulk file access")]
    print(sequence([firewall, auth, fileserver]))
    print("dwell seconds:", dwell_time([firewall, auth, fileserver]))
