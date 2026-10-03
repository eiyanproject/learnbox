---
title: Reading disassembly
summary: Disassembly is the instructions a CPU runs. You do not need to write assembly to read the control flow and find the calls that matter.
order: 3
files: [disasm.py]
run: python disasm.py
hints:
  - "Each instruction is a dict with `addr`, `mnemonic` and `operands`. A function call has mnemonic `call` and its target in `operands`."
  - "`find_calls`: return `(addr, target)` for every `call` instruction."
  - "`calls_function`: whether any `call` targets the given name."
  - "`control_flow_targets`: the destinations of jumps and calls - mnemonics starting with `j` (jmp, je, jne...) or equal to `call`. These are where execution can go."
---

**Disassembly** is a program's machine code translated back into the
instructions the CPU runs - `mov`, `cmp`, `call`, `jmp`. You do not need to
write assembly to get enormous value from reading it: following the **control
flow** and spotting the **calls** is enough to understand what a function does
and where it is vulnerable.

## The shape of an instruction

Each line of disassembly is an **address**, a **mnemonic** (the operation), and
its **operands**:

```text
401136:  lea    rax, [rbp-0x10]
40113a:  mov    rdi, rax
40113d:  call   gets
401142:  test   rax, rax
401145:  je     401160
```

Read top to bottom: the address of a 16-byte buffer on the stack (`rbp-0x10`)
is passed to `gets` as its argument (`rdi`), and if `gets` returns 0 - nothing
read - the code jumps to `401160`. That one `call gets` is already a finding,
as the next lesson explains.

The two that drive everything:

- **`call`** - invokes a function. The operand is the target, and the list of
  call targets is what the function actually *does*.
- **`jmp` / `je` / `jne` / `jz`...** - conditional and unconditional jumps, which
  are branches, loops and `if` statements. These are the points where execution
  can go somewhere other than the next line.

## Reading, not writing

You are not reconstructing the source - you are answering questions: does this
function call `system`? what decides whether it jumps to the failure path? where
does control go from here? That is the level at which most vulnerabilities are
found, and it is why `objdump -d` and a debugger's disassembly view are an
analyst's daily tools. Here you work the instruction list directly.

## Your turn

Each instruction is `{addr, mnemonic, operands}`. In `disasm.py`:

- `find_calls(instrs)` - a list of `(addr, target)` for every `call`, in order,
  where `target` is the `operands` string as it stands
- `calls_function(instrs, name)` - does any `call` target `name`?
- `control_flow_targets(instrs)` - the set of `operands` of every call and every
  jump, where a jump is any mnemonic starting with `j` (`jmp`, `je`, `jne`...)
