DANGERS = {
    "gets": "no bound on input - guaranteed overflow",
    "strcpy": "copies with no size limit",
    "strcat": "appends with no size limit",
    "sprintf": "formats into a buffer with no size bound",
    "system": "passes a string to the shell",
    "scanf": "reads an unbounded string with %s",
}

SAFER = {
    "gets": "fgets", "strcpy": "strncpy", "strcat": "strncat",
    "sprintf": "snprintf", "system": "execve", "scanf": "scanf with a width",
}


def dangerous_calls(called):
    pass


def safer_alternative(name):
    pass


def review(functions):
    pass


if __name__ == "__main__":
    code = {"read_name": ["printf", "gets"], "greet": ["printf"]}
    print("risky functions:", review(code))
    print("fix for gets:", safer_alternative("gets"))
