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
    # The PNG ends at IEND plus its 4-byte CRC. Anything past that was appended
    # and is invisible to an image viewer.
    marker = png.find(b"IEND")
    if marker == -1:
        return b""
    end = marker + 4 + 4   # the IEND type, then its CRC
    return png[end:]


def extract_lsb(pixels):
    # Read the low bit of each byte, pack eight into a character (high bit
    # first), and stop at the null terminator the embedder wrote.
    chars = []
    bits = []
    for byte in pixels:
        bits.append(byte & 1)
        if len(bits) == 8:
            value = 0
            for bit in bits:
                value = (value << 1) | bit
            if value == 0:
                break
            chars.append(chr(value))
            bits = []
    return "".join(chars)


if __name__ == "__main__":
    carrier = bytes(200)
    stego = embed_lsb(carrier, "hi there")
    print("recovered:", extract_lsb(stego))
