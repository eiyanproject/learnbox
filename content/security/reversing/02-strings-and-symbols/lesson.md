---
title: Strings and symbols
summary: Before any disassembly, the readable text and the symbol table tell you most of what a binary does.
order: 2
files: [symbols.py]
run: python symbols.py
hints:
  - "`extract_strings`: collect runs of printable bytes (32..126) at least `min_len` long - the same idea as the environment lesson."
  - "`find_symbol`: the symbol table is a list of `(name, address)`; return the address for a name, or None."
  - "`imported_danger`: return the subset of symbol names that are in the `RISKY` set - library functions worth a closer look."
  - "A binary that imports `system` and `gets` is telling you where to look before you read a single instruction."
---

Reverse engineering does not start with disassembly. It starts with the two
cheapest sources of information in any binary: the **strings** it contains and
the **symbols** it uses. Together they often reveal the purpose and the weak
points before you read a single instruction.

## Strings

Error messages, file paths, URLs, format strings, and sometimes hard-coded
secrets are all stored as plain text. `strings` (which you built in the
environment section) pulls them out, and they sketch what the program does: a
path to a config file, a database connection string, a suspicious URL.

## Symbols

The **symbol table** names the functions - both the program's own and the
library functions it **imports**. That import list is a map of the program's
capabilities: a binary that imports `socket` and `connect` talks to the network;
one that imports `system` runs shell commands; one that imports `gets` has a
buffer waiting to overflow (the next two lessons). Reading the imports tells you
where to aim.

Real tools are `nm`, `readelf -s` and `strings`; here you work with the symbol
list directly to learn what they surface.

## Your turn

`RISKY` (a set of dangerous imports) is provided. In `symbols.py`:

- `extract_strings(data, min_len=4)` - the printable runs in the bytes
- `find_symbol(symbols, name)` - the address for a symbol name, or `None`
  (symbols is a list of `(name, address)`)
- `imported_danger(symbols)` - the set of imported names that are in `RISKY`
