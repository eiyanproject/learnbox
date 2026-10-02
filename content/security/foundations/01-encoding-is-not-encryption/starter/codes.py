def xor_bytes(data, key):
    # XOR data with key, repeating key as needed. Returns bytes.
    pass


def looks_like_text(data):
    # True when data is plausibly an English sentence.
    pass


def break_single_byte_xor(data):
    # Return (key, plaintext) for the single key byte that decodes to text.
    pass


if __name__ == "__main__":
    secret = xor_bytes(b"meet me at dawn", b"K")
    print("scrambled:", secret)
    print("recovered:", break_single_byte_xor(secret))
