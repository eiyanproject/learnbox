from datetime import datetime


def parse(line):
    """(when, ip) for a FAILED line, or None for anything else."""
    parts = line.split()
    if len(parts) != 4 or parts[1] != "FAILED":
        return None
    if not parts[2].startswith("user=") or not parts[3].startswith("ip="):
        return None
    try:
        when = datetime.fromisoformat(parts[0])
    except ValueError:
        return None
    ip = parts[3][len("ip="):]
    return (when, ip) if ip else None


def suspects(lines, threshold=5, window=60):
    failures = {}
    for line in lines:
        event = parse(line)
        if event:
            failures.setdefault(event[1], []).append(event[0])

    found = []
    for ip, times in failures.items():
        times.sort()
        for i in range(len(times) - threshold + 1):
            if (times[i + threshold - 1] - times[i]).total_seconds() <= window:
                found.append(ip)
                break
    return sorted(found)
