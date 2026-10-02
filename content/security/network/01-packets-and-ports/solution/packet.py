import struct

FLAGS = [(1, "FIN"), (2, "SYN"), (4, "RST"), (8, "PSH"), (16, "ACK"), (32, "URG")]


def parse_ipv4(data):
    # The documented IPv4 layout. The low nibble of byte 0 is the header length
    # in 32-bit words; the addresses are four bytes each, written out dotted.
    ver = data[0] >> 4
    ihl = (data[0] & 0x0F) * 4
    protocol = data[9]
    src = ".".join(str(b) for b in data[12:16])
    dst = ".".join(str(b) for b in data[16:20])
    return {"version": ver, "ihl": ihl, "protocol": protocol, "src": src, "dst": dst}


def tcp_flag_names(flags_byte):
    return {name for bit, name in FLAGS if flags_byte & bit}


def parse_tcp(data):
    # Ports are the first two 16-bit big-endian fields; the flags live in the
    # low byte of the 13th byte pair (offset 13).
    src_port = int.from_bytes(data[0:2], "big")
    dst_port = int.from_bytes(data[2:4], "big")
    return {"src_port": src_port, "dst_port": dst_port,
            "flags": tcp_flag_names(data[13])}


def is_syn_only(flags_byte):
    # Exactly SYN, nothing else: a connection attempt, and the packet a scanner
    # sprays across a range of ports to see which answer.
    return tcp_flag_names(flags_byte) == {"SYN"}


if __name__ == "__main__":
    print(tcp_flag_names(0x12), "<- SYN+ACK")
    print("bare SYN only?", is_syn_only(0x02))
