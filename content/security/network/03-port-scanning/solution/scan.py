def open_ports(responses):
    # A completed handshake (SYN+ACK) means a service is listening; RST means
    # the port is closed. Filtered ports simply never appear here.
    found = [port for port, flags in responses if {"SYN", "ACK"} <= flags]
    return sorted(found)


def detect_scan(attempts, threshold=10):
    # The signature is fan-out: one source touching many distinct ports. A
    # legitimate client talks to the one or two it actually needs.
    ports_by_src = {}
    for src, port in attempts:
        ports_by_src.setdefault(src, set()).add(port)
    return {src for src, ports in ports_by_src.items() if len(ports) > threshold}


if __name__ == "__main__":
    replies = [(22, {"SYN", "ACK"}), (23, {"RST"}), (80, {"SYN", "ACK"})]
    print("open:", open_ports(replies))
    probes = [("10.0.0.9", p) for p in range(1, 30)]
    print("scanners:", detect_scan(probes))
