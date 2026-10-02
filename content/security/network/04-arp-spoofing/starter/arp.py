def build_table(packets):
    pass


def detect_conflict(packets):
    pass


def detect_gateway_takeover(packets, gateway_ip, real_mac):
    pass


if __name__ == "__main__":
    traffic = [
        ("192.168.0.1", "aa:aa:aa:aa:aa:aa"),   # the real gateway
        ("192.168.0.5", "bb:bb:bb:bb:bb:bb"),
        ("192.168.0.1", "ee:ee:ee:ee:ee:ee"),   # an attacker claiming it
    ]
    print("conflicts:", detect_conflict(traffic))
    print("takeover?", detect_gateway_takeover(traffic, "192.168.0.1", "aa:aa:aa:aa:aa:aa"))
