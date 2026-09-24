import ipaddress


def _net(route):
    return ipaddress.ip_network(route["network"])


def matching(routes, ip):
    addr = ipaddress.ip_address(ip)
    return [r for r in routes if addr in _net(r)]


def _rank(route):
    # Sorted ascending, so longer prefixes must compare smaller: negate it.
    return (-_net(route).prefixlen, route["distance"], route["metric"])


def best_route(routes, ip):
    candidates = matching(routes, ip)
    if not candidates:
        return None
    return min(candidates, key=_rank)


def is_default(route):
    return _net(route).prefixlen == 0


def beats(a, b):
    return _rank(a) < _rank(b)
