from recover import recover_admin_token
from data import MY_TOKEN


def test_recovers_the_admin_token():
    assert recover_admin_token(MY_TOKEN, 3) == 2653228291


def test_none_when_no_seed_fits():
    assert recover_admin_token(MY_TOKEN, 3, lo=1, hi=10) is None


def test_works_at_a_different_position():
    import random
    r = random.Random(1500)
    issued = [r.getrandbits(32) for _ in range(4)]
    # token #4 for seed 1500 -> admin #1 is the first from 1500
    assert recover_admin_token(issued[3], 4) == random.Random(1500).getrandbits(32)
