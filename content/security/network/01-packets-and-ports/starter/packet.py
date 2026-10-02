import struct

FLAGS = [(1, "FIN"), (2, "SYN"), (4, "RST"), (8, "PSH"), (16, "ACK"), (32, "URG")]


def parse_ipv4(data):
    pass


def tcp_flag_names(flags_byte):
    pass


def parse_tcp(data):
    pass


def is_syn_only(flags_byte):
    pass


if __name__ == "__main__":
    print(tcp_flag_names(0x12), "<- SYN+ACK")
    print("bare SYN only?", is_syn_only(0x02))
