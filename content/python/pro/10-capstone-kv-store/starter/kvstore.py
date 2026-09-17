import json
import os
import sys
import threading


class KVStore:
    def __init__(self, path):
        self.path = os.fspath(path)

    def set(self, key, value):
        pass

    def get(self, key, default=None):
        pass

    def delete(self, key):
        pass

    def keys(self):
        pass

    def log_entries(self):
        pass

    def compact(self):
        pass

    def close(self):
        pass


def main(argv):
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
