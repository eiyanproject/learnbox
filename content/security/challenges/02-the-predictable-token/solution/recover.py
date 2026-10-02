import random
from data import MY_TOKEN


def recover_admin_token(my_token, my_position, lo=1000, hi=2000):
    for seed in range(lo, hi + 1):
        r = random.Random(seed)
        issued = [r.getrandbits(32) for _ in range(my_position)]
        if issued[-1] == my_token:
            # Seed found: the admin's token is the first this seed produces.
            return random.Random(seed).getrandbits(32)
    return None


if __name__ == "__main__":
    print("admin token:", recover_admin_token(MY_TOKEN, 3))
