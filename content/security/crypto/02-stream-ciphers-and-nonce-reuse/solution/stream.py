import hashlib
import secrets


def keystream(key, nonce, length):
    # Counter mode: hash (key, nonce, i) for i = 0, 1, 2... and glue the
    # digests together. Each nonce gives a completely different stream.
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(key + nonce + counter.to_bytes(8, "big")).digest()
        counter += 1
    return out[:length]


def stream_xor(key, nonce, data):
    stream = keystream(key, nonce, len(data))
    return bytes(d ^ k for d, k in zip(data, stream))


def recover_xor_of_plaintexts(c1, c2):
    # The attack on a reused nonce: XOR the ciphertexts and the shared keystream
    # cancels, leaving p1 XOR p2 with no key in sight.
    return bytes(a ^ b for a, b in zip(c1, c2))


def safe_encrypt(key, data):
    # A fresh nonce every time is the whole defence. It is returned, not
    # hidden: the nonce is not secret, only its uniqueness matters.
    nonce = secrets.token_bytes(16)
    return nonce, stream_xor(key, nonce, data)


if __name__ == "__main__":
    key = b"a 16-byte key!!!"
    nonce, ct = safe_encrypt(key, b"attack at dawn")
    print("ciphertext:", ct.hex())
    print("decrypts to:", stream_xor(key, nonce, ct))
