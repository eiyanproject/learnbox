def mode_to_rwx(mode):
    # Three groups of three bits. Each group is one octal digit, and within it
    # the values 4/2/1 are read/write/execute.
    out = []
    for shift in (6, 3, 0):
        bits = (mode >> shift) & 7
        out.append("r" if bits & 4 else "-")
        out.append("w" if bits & 2 else "-")
        out.append("x" if bits & 1 else "-")
    return "".join(out)


def is_world_writable(mode):
    # 0o002 is the write bit for "other" - everyone who is not the owner or in
    # the group. A world-writable file is one anyone can replace.
    return bool(mode & 0o002)


def is_too_open_for_secret(mode):
    # A secret's bar is the strictest there is: owner-only. 0o077 is every bit
    # outside the owner's, so any of them being set is already too much.
    return bool(mode & 0o077)


def tighten(mode):
    # Least privilege applied: keep the owner's bits, drop everyone else's.
    return mode & 0o700


if __name__ == "__main__":
    for m in [0o644, 0o600, 0o777, 0o640]:
        print(f"{m:04o}  {mode_to_rwx(m)}  secret_leak={is_too_open_for_secret(m)}")
