SAVED_BP = 8   # bytes, x86-64


def offset_to_return(buffer_size):
    # Past the buffer, then past the 8-byte saved base pointer, lies the return
    # address.
    return buffer_size + SAVED_BP


def overflows_buffer(input_len, buffer_size):
    return input_len > buffer_size


def reaches_return_address(input_len, buffer_size):
    # The input must cover the buffer and the saved base pointer before any of
    # it lands on the return address.
    return input_len > buffer_size + SAVED_BP


if __name__ == "__main__":
    print("a 64-byte buffer: return address at offset", offset_to_return(64))
    print("72 bytes reaches it?", reaches_return_address(72, 64))
