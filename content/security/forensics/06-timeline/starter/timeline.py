from datetime import datetime


def merge(sources):
    pass


def sequence(sources):
    pass


def dwell_time(sources):
    pass


if __name__ == "__main__":
    firewall = [("2026-01-02T03:00:00", "fw", "port scan from 10.0.0.9")]
    auth = [("2026-01-02T03:05:00", "sshd", "brute-force login succeeded")]
    fileserver = [("2026-01-02T03:20:00", "nfs", "bulk file access")]
    print(sequence([firewall, auth, fileserver]))
    print("dwell seconds:", dwell_time([firewall, auth, fileserver]))
