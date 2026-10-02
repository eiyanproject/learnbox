import hashlib


def baseline(files):
    # One digest per file: ground truth taken on a trusted system.
    return {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def compare(base, current):
    # Three kinds of change, each an alarm in its own right.
    changed = [n for n in base if n in current and base[n] != current[n]]
    added = [n for n in current if n not in base]
    removed = [n for n in base if n not in current]
    return {"changed": sorted(changed), "added": sorted(added),
            "removed": sorted(removed)}


if __name__ == "__main__":
    good = baseline({"/bin/login": b"original", "/etc/hosts": b"127.0.0.1 localhost"})
    now = baseline({"/bin/login": b"BACKDOORED", "/etc/hosts": b"127.0.0.1 localhost",
                    "/tmp/shell": b"evil"})
    print(compare(good, now))
