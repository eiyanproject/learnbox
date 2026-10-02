def hexdump(data):
    # xxd-style lines: offset, hex bytes, then the ASCII column.
    pass


def find_strings(data, min_len=4):
    # Printable runs of at least min_len bytes, as strings, in order.
    pass


if __name__ == "__main__":
    print(hexdump(b"\x7fELF\x02\x01hello"))
    print(find_strings(b"\x00\x01password\x00\xffok\x00"))
