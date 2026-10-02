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
    # Each block on its own. The flaw falls straight out: give it the same
    # block twice and you get the same ciphertext twice.
    return b"".join(block_transform(key, b) for b in chunks(data, bs))


def has_repeated_blocks(data, bs=16):
    blocks = chunks(data, bs)
    return len(set(blocks)) != len(blocks)


def cbc_encrypt(key, iv, data, bs=16):
    # Each plaintext block is XORed with the previous ciphertext block before
    # the cipher, so equal plaintext blocks diverge after the first.
    out = []
    prev = iv
    for block in chunks(data, bs):
        mixed = bytes(b ^ p for b, p in zip(block, prev))
        c = block_transform(key, mixed)
        out.append(c)
        prev = c
    return b"".join(out)


if __name__ == "__main__":
    key = bytes(range(16))
    plain = b"YELLOW SUBMARINE" * 3   # three identical blocks
    print("ECB repeats?", has_repeated_blocks(ecb_encrypt(key, plain)))
    iv = bytes(16)
    print("CBC repeats?", has_repeated_blocks(cbc_encrypt(key, iv, plain)))
