import hashlib
import secrets


def keystream(key, nonce, length):
    pass


def stream_xor(key, nonce, data):
    pass


def recover_xor_of_plaintexts(c1, c2):
    pass


def safe_encrypt(key, data):
    pass


if __name__ == "__main__":
    key = b"a 16-byte key!!!"
    nonce, ct = safe_encrypt(key, b"attack at dawn")
    print("ciphertext:", ct.hex())
    print("decrypts to:", stream_xor(key, nonce, ct))
