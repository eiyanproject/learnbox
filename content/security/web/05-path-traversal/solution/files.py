import os


def serve_vulnerable(root, name):
    # VULNERABLE: the name is joined on and opened, so ../ walks out of root.
    return open(os.path.join(root, name)).read()


def traversal_payload():
    # One step up from the web root reaches the secret the test places there.
    return "../secret.txt"


def serve_safe(root, name):
    # Resolve first, then confine: realpath collapses .. and symlinks to the
    # true location, and only then do we check it is still under the root.
    base = os.path.realpath(root)
    full = os.path.realpath(os.path.join(root, name))
    if full != base and not full.startswith(base + os.sep):
        raise ValueError("outside the web root")
    return open(full).read()


if __name__ == "__main__":
    print("payload:", traversal_payload())
