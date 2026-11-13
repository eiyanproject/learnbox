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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **machine code** | the bytes a processor actually executes |
| **assembly** | machine code written as readable instructions, one per line |
| **disassembly** | turning machine code back into assembly |
| **instruction** | one step for the processor, such as "compare" or "call" |
| **address** | where an instruction sits in memory, such as `401146` |
| **mnemonic** | the instruction's short name: `mov`, `cmp`, `call`, `jmp` |
| **operand** | what the instruction works on: a register, a number, an address |
| **register** | a small, very fast storage slot inside the processor: `rax`, `rdi`, `rsp` |
| **`mov a, b`** | copy `b` into `a` |
| **`test a, a`**, **`cmp a, b`** | compare, setting flags that the next jump reads |
| **`call f`** | run function `f`, then come back |
| **`ret`** | return from the current function |
| **`jmp x`** | always continue at `x` |
| **`je x`** / **`jz x`** | jump to `x` if the last comparison was equal (zero) |
| **`jne x`** / **`jnz x`** | jump if it was not equal |
| **conditional jump** | a jump that depends on a comparison: how `if` statements look in assembly |
| **control flow** | the paths execution can take through a function |
| **branch** | a point where the path splits |
| **calling convention** | the rule for passing arguments; on Linux x86-64 the first goes in `rdi`, the second in `rsi`, and the result comes back in `rax` (`eax` is its lower half) |
| **`@plt`** | marks a call into a library function, such as `strcmp@plt` |
| **Intel syntax** | the assembly style used here: destination first (`mov rdi, rax`) |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `objdump -d -M intel file` | disassembles a binary, in Intel syntax |
| `objdump -d -M intel --no-show-raw-insn file` | the same without the raw bytes column |
| `python disasm.py` | runs your program: lists the calls in a short instruction list |

### Python names

| Name | What it does |
|---|---|
| `{"addr": ..., "mnemonic": ..., "operands": ...}` | one instruction, as a dict |
| `[(i["addr"], i["operands"]) for i in instrs if ...]` | address and target of each instruction that passes the test |
| `i["mnemonic"] == "call"` | the instruction is a call |
| `m.startswith("j")` | the instruction is a jump (`jmp`, `je`, `jne`, ...) |
| `any(...)` | `True` if at least one instruction passes |
| `targets.add(...)` | adds to a set; repeats are ignored |

---

**Disassembly** is a program's machine code turned back into the
instructions the processor runs: `mov`, `cmp`, `call`, `jmp`. You do not need
to write assembly to get a great deal out of reading it. Following the
**control flow** and spotting the **calls** is enough to understand what a
function does, and where it is weak.

## A real function

Here is a small C function that checks a PIN:

```c
int check(const char *pin) {
    if (strcmp(pin, "4921") == 0) {
        puts("access granted");
        return 1;
    }
    puts("wrong pin");
    return 0;
}
```

Compiled and then disassembled with `objdump -d -M intel`, it becomes:

```text
0000000000401146 <check>:
  401146:  sub    rsp,0x8
  40114a:  mov    esi,0x402004
  40114f:  call   401040 <strcmp@plt>
  401154:  test   eax,eax
  401156:  je     40116c <check+0x26>
  401158:  mov    edi,0x402018
  40115d:  call   401030 <puts@plt>
  401162:  mov    eax,0x0
  401167:  add    rsp,0x8
  40116b:  ret
  40116c:  mov    edi,0x402009
  401171:  call   401030 <puts@plt>
  401176:  mov    eax,0x1
  40117b:  jmp    401167 <check+0x21>
```

Each line is an **address**, a **mnemonic** (the operation) and its
**operands**.

## Reading it

You need only a few facts. On Linux x86-64, a function's first argument goes
in the register `rdi`, the second in `rsi`, and its result comes back in `rax`
(`eax` is the lower half of `rax`). In Intel syntax the destination comes
first: `mov esi, 0x402004` puts `0x402004` into `esi`.

Now read from the top:

1. `mov esi, 0x402004`: the second argument for the next call is the address
   `0x402004`. That is where the text `"4921"` is stored. (The first argument,
   the user's PIN, is already in `rdi`.)
2. `call strcmp`: compare the two strings.
3. `test eax, eax` then `je 40116c`: if `strcmp` returned 0 (the strings are
   equal), jump to `40116c`.
4. Not equal: print one message (`call puts`), put 0 in `eax`, return.
5. Equal, at `40116c`: print the other message, put 1 in `eax`, and jump back
   to the shared return.

Without the source, you would know: this function compares the input with a
fixed string and returns 1 or 0. And `strings` on the same file would show
`4921` sitting there: a **hard-coded secret**, found with no source at all.

## The two instructions that matter most

- **`call`** runs a function. The list of call targets is what a function
  actually **does**: here, `strcmp` and `puts`.
- **Jumps** are `jmp` (always) and the conditional ones, `je`, `jne`, `jz`,
  `jnz` and more, all starting with `j`. They are the branches, loops and `if`
  statements: the only places execution can go somewhere other than the next
  line.

Together, the call and jump targets map where execution can go: the
**control flow**.

## Reading, not writing

You are not rebuilding the source code. You are answering questions:

- Does this function call `system` or `gets`?
- What decides whether it takes the failure path?
- Where can control go from here?

That is the level at which most vulnerabilities are found, which is why
`objdump -d` and a debugger's disassembly view are an analyst's daily tools.
In this exercise you work on the instruction list directly.

## Your turn

Each instruction is a dict `{addr, mnemonic, operands}`. In `disasm.py`:

- `find_calls(instrs)`: a list of `(addr, target)` for every `call`, in order,
  where `target` is the `operands` string as it is.
- `calls_function(instrs, name)`: does any `call` target `name`?
- `control_flow_targets(instrs)`: the set of `operands` of every call and every
  jump, where a jump is any mnemonic starting with `j`.

Run it:

```text
calls: [(4198715, 'gets')]
calls gets? True
```

(`4198715` is `0x40113b`.)

## Check yourself

1. In `mov esi, 0x402004`, which is the destination?
   *`esi`: Intel syntax puts the destination first.*
2. Which register holds a function's result on Linux x86-64?
   *`rax` (`eax` for 32 bits).*
3. What does `je 40116c` after `test eax, eax` do?
   *Jumps to `40116c` if `eax` is zero.*
4. How would you find the PIN in this binary without disassembling it?
   *`strings`: it is stored as plain text.*
5. Which mnemonics are jumps?
   *All those starting with `j`: `jmp`, `je`, `jne`, `jz` and so on.*
