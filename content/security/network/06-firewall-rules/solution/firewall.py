FIELDS = ("proto", "src", "dst_port")


def matches(rule, packet):
    # A field the rule leaves out (or sets to None) is a wildcard; a field it
    # specifies must equal the packet's.
    for field in FIELDS:
        wanted = rule.get(field)
        if wanted is not None and wanted != packet.get(field):
            return False
    return True


def evaluate(rules, packet, default="deny"):
    # First match wins, so order is meaning. Nothing matched means the
    # default - and the only safe default is deny.
    for rule in rules:
        if matches(rule, packet):
            return rule["action"]
    return default


if __name__ == "__main__":
    rules = [
        {"action": "allow", "proto": "tcp", "src": "10.0.0.5", "dst_port": 22},
        {"action": "allow", "proto": "tcp", "dst_port": 443},
    ]
    print(evaluate(rules, {"proto": "tcp", "src": "10.0.0.5", "dst_port": 22}))
    print(evaluate(rules, {"proto": "tcp", "src": "1.2.3.4", "dst_port": 22}))
