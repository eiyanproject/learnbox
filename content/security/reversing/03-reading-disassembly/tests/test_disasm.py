from disasm import find_calls, calls_function, control_flow_targets

CODE = [
    {"addr": 0x401130, "mnemonic": "push", "operands": "rbp"},
    {"addr": 0x401136, "mnemonic": "mov", "operands": "edi, 0x402004"},
    {"addr": 0x40113b, "mnemonic": "call", "operands": "gets"},
    {"addr": 0x401140, "mnemonic": "cmp", "operands": "eax, 0x0"},
    {"addr": 0x401147, "mnemonic": "je", "operands": "401160"},
    {"addr": 0x40114d, "mnemonic": "call", "operands": "system"},
    {"addr": 0x401152, "mnemonic": "jmp", "operands": "401170"},
]


def test_find_calls():
    assert find_calls(CODE) == [(0x40113b, "gets"), (0x40114d, "system")]


def test_find_calls_none():
    assert find_calls([{"addr": 1, "mnemonic": "nop", "operands": ""}]) == []


def test_calls_function_true():
    assert calls_function(CODE, "gets")
    assert calls_function(CODE, "system")


def test_calls_function_false():
    assert not calls_function(CODE, "printf")


def test_control_flow_targets():
    assert control_flow_targets(CODE) == {"gets", "system", "401160", "401170"}


def test_control_flow_includes_conditional_jumps():
    code = [{"addr": 1, "mnemonic": "jne", "operands": "4010a0"}]
    assert control_flow_targets(code) == {"4010a0"}


def test_control_flow_ignores_plain_instructions():
    code = [{"addr": 1, "mnemonic": "mov", "operands": "eax, ebx"},
            {"addr": 2, "mnemonic": "add", "operands": "eax, 1"}]
    assert control_flow_targets(code) == set()
