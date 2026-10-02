def xor_bytes(data, key):
    # key[i % len(key)] cycles the key across the data. XOR is symmetric, so
    # this one function is both the encrypt and the decrypt direction.
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def looks_like_text(data):
    # The giveaway of English is spaces: they are the most common character and
    # appear every few letters. Noise from a wrong key rarely has that.
    if not data:
        return False
    printable = sum(1 for b in data if 32 <= b <= 126)
    if printable < len(data) * 0.95:
        return False
    return b" " in data


def break_single_byte_xor(data):
    # Only 256 keys exist, so trying all of them is instant. The work is not
    # the search - it is recognising the one real answer among the noise.
    best = None
    best_score = -1
    for key in range(256):
        candidate = xor_bytes(data, bytes([key]))
        if not looks_like_text(candidate):
            continue
        # Prefer the decode that reads most like text: letters and spaces.
        score = sum(1 for b in candidate if b == 32 or chr(b).isalpha())
        if score > best_score:
            best_score = score
            best = (key, candidate.decode())
    return best


if __name__ == "__main__":
    secret = xor_bytes(b"meet me at dawn", b"K")
    print("scrambled:", secret)
    print("recovered:", break_single_byte_xor(secret))
