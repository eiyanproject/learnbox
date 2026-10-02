FIELDS = ("proto", "src", "dst_port")


def matches(rule, packet):
    pass


def evaluate(rules, packet, default="deny"):
    pass


if __name__ == "__main__":
    rules = [
        {"action": "allow", "proto": "tcp", "src": "10.0.0.5", "dst_port": 22},
        {"action": "allow", "proto": "tcp", "dst_port": 443},
    ]
    print(evaluate(rules, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22}))
    print(evaluate(rules, {"proto": "tcp", "src": "1.2.3.4", "dst_port": 22}))
