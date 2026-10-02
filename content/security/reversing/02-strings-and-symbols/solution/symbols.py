RISKY = {"system", "exec", "gets", "strcpy", "strcat", "sprintf", "scanf", "popen"}


def extract_strings(data, min_len=4):
    found, run = [], []
    for b in data:
        if 32 <= b <= 126:
            run.append(chr(b))
        else:
            if len(run) >= min_len:
                found.append("".join(run))
            run = []
    if len(run) >= min_len:
        found.append("".join(run))
    return found


def find_symbol(symbols, name):
    for sym_name, addr in symbols:
        if sym_name == name:
            return addr
    return None


def imported_danger(symbols):
    # The import list is a map of capabilities; the risky subset is where to
    # look first, before reading any instructions.
    return {name for name, _ in symbols if name in RISKY}


if __name__ == "__main__":
    syms = [("main", 0x401050), ("gets", 0x401030), ("printf", 0x401040)]
    print("risky imports:", imported_danger(syms))
