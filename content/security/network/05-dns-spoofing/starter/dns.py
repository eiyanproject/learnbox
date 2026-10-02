import struct


def parse_header(data):
    pass


def accept_response(pending, response):
    pass


if __name__ == "__main__":
    # id=0x1234, flags=0x8180 (a standard response), 1 question, 1 answer
    hdr = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0)
    print(parse_header(hdr))
    pending = {(0x1234, "example.com")}
    print(accept_response(pending, (0x1234, "example.com", True, "93.184.216.34")))
    print(accept_response(pending, (0x9999, "example.com", True, "6.6.6.6")))
