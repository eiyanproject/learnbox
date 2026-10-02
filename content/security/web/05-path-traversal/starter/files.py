import os


def serve_vulnerable(root, name):
    # VULNERABLE: the name is joined on and opened, so ../ walks out of root.
    return open(os.path.join(root, name)).read()


def traversal_payload():
    # Return a name that escapes the web root to the file one level above it.
    pass


def serve_safe(root, name):
    # Serve only files that resolve to a location inside root.
    pass


if __name__ == "__main__":
    print("payload:", traversal_payload())
