from stream import keystream, stream_xor, recover_xor_of_plaintexts, safe_encrypt


def test_keystream_length():
    assert len(keystream(b"k", b"n", 100)) == 100


def test_keystream_is_deterministic():
    assert keystream(b"k", b"n", 50) == keystream(b"k", b"n", 50)


def test_keystream_changes_with_nonce():
    assert keystream(b"k", b"n1", 32) != keystream(b"k", b"n2", 32)


def test_keystream_changes_with_key():
    assert keystream(b"k1", b"n", 32) != keystream(b"k2", b"n", 32)


def test_stream_xor_round_trips():
    key, nonce, msg = b"secret-key", b"nonce-1", b"attack at dawn"
    ct = stream_xor(key, nonce, msg)
    assert stream_xor(key, nonce, ct) == msg


def test_stream_xor_actually_hides():
    assert stream_xor(b"k", b"n", b"plaintext here") != b"plaintext here"


def test_nonce_reuse_leaks_xor_of_plaintexts():
    key, nonce = b"shared-key", b"reused-nonce"
    p1 = b"the eagle lands at noon!"
    p2 = b"the sparrow flies at six"
    c1 = stream_xor(key, nonce, p1)
    c2 = stream_xor(key, nonce, p2)
    leaked = recover_xor_of_plaintexts(c1, c2)
    assert leaked == bytes(a ^ b for a, b in zip(p1, p2))


def test_knowing_one_plaintext_reveals_the_other():
    # With p1 XOR p2 and p1 known, p2 falls out by XOR.
    key, nonce = b"k", b"n"
    p1, p2 = b"GET /index.html ", b"GET /secret.html"
    leaked = recover_xor_of_plaintexts(stream_xor(key, nonce, p1), stream_xor(key, nonce, p2))
    recovered = bytes(a ^ b for a, b in zip(leaked, p1))
    assert recovered == p2


def test_safe_encrypt_uses_a_fresh_nonce():
    key, msg = b"key", b"same message"
    n1, _ = safe_encrypt(key, msg)
    n2, _ = safe_encrypt(key, msg)
    assert n1 != n2


def test_safe_encrypt_ciphertexts_differ_for_same_message():
    key, msg = b"key", b"same message"
    _, c1 = safe_encrypt(key, msg)
    _, c2 = safe_encrypt(key, msg)
    assert c1 != c2


def test_safe_encrypt_decrypts():
    key, msg = b"key", b"recover me exactly"
    nonce, ct = safe_encrypt(key, msg)
    assert stream_xor(key, nonce, ct) == msg
