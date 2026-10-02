def find_calls(instrs):
    pass


def calls_function(instrs, name):
    pass


def control_flow_targets(instrs):
    pass


if __name__ == "__main__":
    code = [
        {"addr": 0x401136, "mnemonic": "mov", "operands": "edi, 0x402004"},
        {"addr": 0x40113b, "mnemonic": "call", "operands": "gets"},
        {"addr": 0x401147, "mnemonic": "je", "operands": "401160"},
    ]
    print("calls:", find_calls(code))
    print("calls gets?", calls_function(code, "gets"))
