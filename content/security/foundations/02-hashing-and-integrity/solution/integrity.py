import hashlib
import hmac


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def tampered(data, expected_hex):
    # Integrity in one line: if the recomputed digest differs, the data moved.
    return sha256_hex(data) != expected_hex


def crack(target_hex, words):
    # The attack on an unsalted hash is not reversal - it is a search. Each
    # guess is hashed and compared; a common password falls at once.
    for word in words:
        if sha256_hex(word) == target_hex:
            return word
    return None


def salted_hash(password, salt):
    # The salt makes identical passwords hash differently, so one precomputed
    # table cannot crack every account at once.
    return hashlib.sha256(salt + password).hexdigest()


def verify_hmac(key, message, tag_hex):
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    # compare_digest, not ==: a normal compare leaks, through its timing, how
    # many leading bytes were correct, which is enough to forge a tag.
    return hmac.compare_digest(expected, tag_hex)


if __name__ == "__main__":
    h = sha256_hex(b"password123")
    print("stolen hash:", h)
    print("cracked to:", crack(h, [b"letmein", b"password123", b"qwerty"]))
