"""Top-level worker functions for the tests: process pools can only send picklable callables."""

import os


def inverse(x):
    return 1 / x


def pid_of(_):
    return os.getpid()
