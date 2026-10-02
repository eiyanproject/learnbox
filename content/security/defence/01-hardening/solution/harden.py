RULES = {
    "PermitRootLogin": ("yes", "no"),
    "PasswordAuthentication": ("yes", "no"),
    "X11Forwarding": ("yes", "no"),
    "Protocol": (1, 2),
    "debug": (True, False),
}


def findings(config):
    # A setting is at fault when it holds exactly the known-insecure value.
    return sorted(name for name, (bad, _good) in RULES.items()
                  if config.get(name) == bad)


def harden(config):
    # Review and remediation in one pass: correct every at-fault setting.
    fixed = dict(config)
    for name in findings(config):
        fixed[name] = RULES[name][1]
    return fixed


def is_hardened(config):
    return findings(config) == []


if __name__ == "__main__":
    cfg = {"PermitRootLogin": "yes", "Protocol": 2, "debug": True}
    print("findings:", findings(cfg))
    print("hardened:", harden(cfg))
