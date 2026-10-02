import hashlib


def baseline(files):
    pass


def compare(base, current):
    pass


if __name__ == "__main__":
    good = baseline({"/bin/login": b"original", "/etc/hosts": b"127.0.0.1 localhost"})
    now = baseline({"/bin/login": b"BACKDOORED", "/etc/hosts": b"127.0.0.1 localhost",
                    "/tmp/shell": b"evil"})
    print(compare(good, now))
