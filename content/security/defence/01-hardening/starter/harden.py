RULES = {
    "PermitRootLogin": ("yes", "no"),
    "PasswordAuthentication": ("yes", "no"),
    "X11Forwarding": ("yes", "no"),
    "Protocol": (1, 2),
    "debug": (True, False),
}


def findings(config):
    pass


def harden(config):
    pass


def is_hardened(config):
    pass


if __name__ == "__main__":
    cfg = {"PermitRootLogin": "yes", "Protocol": 2, "debug": True}
    print("findings:", findings(cfg))
    print("hardened:", harden(cfg))
