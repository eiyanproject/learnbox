import struct
from elf_data import SAMPLE_ELF

TYPES = {1: "REL", 2: "EXEC", 3: "DYN"}
MACHINES = {0x3E: "x86-64", 0x28: "ARM", 0xB7: "AArch64"}


def parse_elf(data):
    pass


def is_executable(data):
    pass


def is_pie(data):
    pass


if __name__ == "__main__":
    print(parse_elf(SAMPLE_ELF))
    print("PIE?", is_pie(SAMPLE_ELF))
