def open_ports(responses):
    pass


def detect_scan(attempts, threshold=10):
    pass


if __name__ == "__main__":
    replies = [(22, {"SYN", "ACK"}), (23, {"RST"}), (80, {"SYN", "ACK"})]
    print("open:", open_ports(replies))
    probes = [("10.0.0.9", p) for p in range(1, 30)]
    print("scanners:", detect_scan(probes))
