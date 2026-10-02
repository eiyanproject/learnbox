def find_calls(instrs):
    return [(i["addr"], i["operands"]) for i in instrs if i["mnemonic"] == "call"]


def calls_function(instrs, name):
    return any(i["mnemonic"] == "call" and i["operands"] == name for i in instrs)


def control_flow_targets(instrs):
    # Where execution can go: the destination of every call and every jump.
    # Jumps all start with 'j' (jmp, je, jne, jz, jle...).
    targets = set()
    for i in instrs:
        m = i["mnemonic"]
        if m == "call" or m.startswith("j"):
            targets.add(i["operands"])
    return targets


if __name__ == "__main__":
    code = [
        {"addr": 0x401136, "mnemonic": "mov", "operands": "edi, 0x402004"},
        {"addr": 0x40113b, "mnemonic": "call", "operands": "gets"},
        {"addr": 0x401147, "mnemonic": "je", "operands": "401160"},
    ]
    print("calls:", find_calls(code))
    print("calls gets?", calls_function(code, "gets"))
