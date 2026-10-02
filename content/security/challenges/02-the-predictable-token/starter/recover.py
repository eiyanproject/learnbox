import random
from data import MY_TOKEN


def recover_admin_token(my_token, my_position, lo=1000, hi=2000):
    # Find the seed that yields my_token at my_position, then replay from #1.
    pass


if __name__ == "__main__":
    print("admin token:", recover_admin_token(MY_TOKEN, 3))
