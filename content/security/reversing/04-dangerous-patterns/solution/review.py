DANGERS = {
    "gets": "no bound on input - guaranteed overflow",
    "strcpy": "copies with no size limit",
    "strcat": "appends with no size limit",
    "sprintf": "formats into a buffer with no size bound",
    "system": "passes a string to the shell",
    "scanf": "reads an unbounded string with %s",
}

SAFER = {
    "gets": "fgets", "strcpy": "snprintf", "strcat": "snprintf",
    "sprintf": "snprintf", "system": "execve", "scanf": "scanf with a width",
}


def dangerous_calls(called):
    return {name: DANGERS[name] for name in called if name in DANGERS}


def safer_alternative(name):
    return SAFER.get(name)


def review(functions):
    # A function is risky if any call it makes is on the dangerous list. This
    # is the core of scanning a codebase: find where the hazards are used.
    return {fn for fn, calls in functions.items() if dangerous_calls(calls)}


if __name__ == "__main__":
    code = {"read_name": ["printf", "gets"], "greet": ["printf"]}
    print("risky functions:", review(code))
    print("fix for gets:", safer_alternative("gets"))
