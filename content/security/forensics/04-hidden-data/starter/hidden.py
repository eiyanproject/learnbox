def embed_lsb(pixels, message):
    # Provided: hide message (plus a 0 terminator) in the low bit of each byte.
    bits = []
    for ch in message.encode() + b"\x00":
        bits.extend((ch >> (7 - i)) & 1 for i in range(8))
    out = bytearray(pixels)
    for i, bit in enumerate(bits):
        out[i] = (out[i] & 0xFE) | bit
    return bytes(out)


def data_after_iend(png):
    pass


def extract_lsb(pixels):
    pass


if __name__ == "__main__":
    carrier = bytes(200)
    stego = embed_lsb(carrier, "hi there")
    print("recovered:", extract_lsb(stego))
