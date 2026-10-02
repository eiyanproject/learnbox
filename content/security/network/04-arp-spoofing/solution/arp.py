def build_table(packets):
    # ARP caches trust the most recent reply, which is exactly what makes
    # spoofing work: a later forged answer overwrites the real one.
    table = {}
    for ip, mac in packets:
        table[ip] = mac
    return table


def detect_conflict(packets):
    # One IP legitimately has one MAC. Two distinct MACs claiming it means
    # someone is contending for an address that is not theirs.
    macs_by_ip = {}
    for ip, mac in packets:
        macs_by_ip.setdefault(ip, set()).add(mac)
    return {ip for ip, macs in macs_by_ip.items() if len(macs) > 1}


def detect_gateway_takeover(packets, gateway_ip, real_mac):
    # The highest-value target: redirect the gateway and you see everyone's
    # traffic to the outside world.
    return any(ip == gateway_ip and mac != real_mac for ip, mac in packets)


if __name__ == "__main__":
    traffic = [
        ("192.168.0.1", "aa:aa:aa:aa:aa:aa"),   # the real gateway
        ("192.168.0.5", "bb:bb:bb:bb:bb:bb"),
        ("192.168.0.1", "ee:ee:ee:ee:ee:ee"),   # an attacker claiming it
    ]
    print("conflicts:", detect_conflict(traffic))
    print("takeover?", detect_gateway_takeover(traffic, "192.168.0.1", "aa:aa:aa:aa:aa:aa"))
