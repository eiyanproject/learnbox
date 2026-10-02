def block_transform(key, block):
    # A stand-in for a real block cipher: a deterministic keyed scramble, NOT
    # secure. It is non-linear (a hash) rather than a plain XOR, because a
    # linear transform would make CBC collapse and hide the very point. The
    # lesson is the mode wrapped around it, not this.
    import hashlib
    return hashlib.sha256(key + block).digest()[:len(block)]


def chunks(data, bs):
    return [data[i:i + bs] for i in range(0, len(data), bs)]


def ecb_encrypt(key, data, bs=16):
    pass


def has_repeated_blocks(data, bs=16):
    pass


def cbc_encrypt(key, iv, data, bs=16):
    pass


if __name__ == "__main__":
    key = bytes(range(16))
    plain = b"YELLOW SUBMARINE" * 3   # three identical blocks
    print("ECB repeats?", has_repeated_blocks(ecb_encrypt(key, plain)))
    iv = bytes(16)
    print("CBC repeats?", has_repeated_blocks(cbc_encrypt(key, iv, plain)))
