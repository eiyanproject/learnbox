def mode_to_rwx(mode):
    pass


def is_world_writable(mode):
    pass


def is_too_open_for_secret(mode):
    pass


def tighten(mode):
    pass


if __name__ == "__main__":
    for m in [0o644, 0o600, 0o777, 0o640]:
        print(f"{m:04o}  {mode_to_rwx(m)}  secret_leak={is_too_open_for_secret(m)}")
