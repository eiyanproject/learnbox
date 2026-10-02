import struct
from elf_data import SAMPLE_ELF

TYPES = {1: "REL", 2: "EXEC", 3: "DYN"}
MACHINES = {0x3E: "x86-64", 0x28: "ARM", 0xB7: "AArch64"}


def parse_elf(data):
    magic_ok = data[:4] == b"\x7fELF"
    bits = 64 if data[4] == 2 else 32
    endian = "little" if data[5] == 1 else "big"
    e_type = struct.unpack("<H", data[16:18])[0]
    e_machine = struct.unpack("<H", data[18:20])[0]
    # The entry point is 8 bytes on a 64-bit ELF, 4 on a 32-bit one.
    entry = int.from_bytes(data[24:32] if bits == 64 else data[24:28], "little")
    return {"magic_ok": magic_ok, "bits": bits, "endian": endian,
            "type": TYPES.get(e_type, "?"), "machine": MACHINES.get(e_machine, "?"),
            "entry": entry}


def is_executable(data):
    return parse_elf(data)["type"] in ("EXEC", "DYN")


def is_pie(data):
    # A position-independent executable is type DYN, which is what lets the
    # loader place it at a random address - the basis of ASLR.
    return parse_elf(data)["type"] == "DYN"


if __name__ == "__main__":
    print(parse_elf(SAMPLE_ELF))
    print("PIE?", is_pie(SAMPLE_ELF))
