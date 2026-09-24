import ipaddress


def _net(ip, mask):
    return ipaddress.ip_network(f"{ip}/{mask}", strict=False)


def network_address(ip, mask):
    return str(_net(ip, mask).network_address)


def broadcast_address(ip, mask):
    return str(_net(ip, mask).broadcast_address)


def usable_hosts(prefix):
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2  # RFC 3021: point-to-point links use both addresses
    return 2 ** (32 - prefix) - 2


def same_subnet(a, b, mask):
    return _net(a, mask).network_address == _net(b, mask).network_address


def split(cidr, new_prefix):
    return [str(n) for n in ipaddress.ip_network(cidr).subnets(new_prefix=new_prefix)]
