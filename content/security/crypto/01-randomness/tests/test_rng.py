import random
from rng import secure_token, weak_token, predict, enough_entropy


def test_secure_token_length():
    assert len(secure_token(16)) == 32


def test_secure_token_is_hex():
    assert all(c in "0123456789abcdef" for c in secure_token(8))


def test_secure_tokens_differ():
    assert secure_token() != secure_token()


def test_secure_token_respects_size():
    assert len(secure_token(4)) == 8


def test_weak_token_is_reproducible():
    assert weak_token(42) == weak_token(42)


def test_weak_tokens_differ_by_seed():
    assert weak_token(1) != weak_token(2)


def test_predict_matches_the_generator():
    r = random.Random(1234)
    expected = [r.getrandbits(32) for _ in range(5)]
    assert predict(1234, 5) == expected[-1]


def test_predict_first_equals_weak_token():
    assert predict(99, 1) == weak_token(99)


def test_predict_is_the_whole_attack():
    # Knowing the seed reproduces the server's exact nth token.
    seed = 2026
    r = random.Random(seed)
    issued = [r.getrandbits(32) for _ in range(3)]
    assert predict(seed, 3) == issued[2]


def test_enough_entropy_floor():
    assert enough_entropy(16)
    assert enough_entropy(32)


def test_not_enough_entropy():
    assert not enough_entropy(8)
    assert not enough_entropy(4)
