SAVED_BP = 8   # bytes, x86-64


def offset_to_return(buffer_size):
    pass


def overflows_buffer(input_len, buffer_size):
    pass


def reaches_return_address(input_len, buffer_size):
    pass


if __name__ == "__main__":
    print("a 64-byte buffer: return address at offset", offset_to_return(64))
    print("72 bytes reaches it?", reaches_return_address(72, 64))
