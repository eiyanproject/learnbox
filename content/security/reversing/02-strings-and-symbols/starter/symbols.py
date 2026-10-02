RISKY = {"system", "exec", "gets", "strcpy", "strcat", "sprintf", "scanf", "popen"}


def extract_strings(data, min_len=4):
    pass


def find_symbol(symbols, name):
    pass


def imported_danger(symbols):
    pass


if __name__ == "__main__":
    syms = [("main", 0x401050), ("gets", 0x401030), ("printf", 0x401040)]
    print("risky imports:", imported_danger(syms))
