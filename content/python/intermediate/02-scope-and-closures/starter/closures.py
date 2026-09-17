def make_counter(start=0):
    pass


def make_multiplier(n):
    pass


def make_accumulator():
    pass


def make_adders(n):
    # This has the late-binding bug described in the lesson. Fix it.
    return [lambda x: x + i for i in range(n)]
