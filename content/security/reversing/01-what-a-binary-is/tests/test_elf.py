import struct
from elf import parse_elf, is_executable, is_pie
from elf_data import SAMPLE_ELF


def elf(e_type):
    ident = bytes([0x7F]) + b"ELF" + bytes([2, 1, 1, 0]) + bytes(8)
    return ident + struct.pack("<HHIQQQIHHHHHH", e_type, 0x3E, 1, 0x401050,
                               0, 0, 0, 64, 56, 0, 64, 0, 0)


def test_magic_recognised():
    assert parse_elf(SAMPLE_ELF)["magic_ok"]


def test_not_an_elf():
    assert not parse_elf(b"MZ this is a PE\x00\x00" + bytes(60))["magic_ok"]


def test_sixty_four_bit():
    assert parse_elf(SAMPLE_ELF)["bits"] == 64


def test_little_endian():
    assert parse_elf(SAMPLE_ELF)["endian"] == "little"


def test_machine_is_x86_64():
    assert parse_elf(SAMPLE_ELF)["machine"] == "x86-64"


def test_entry_point():
    assert parse_elf(SAMPLE_ELF)["entry"] == 0x401050


def test_exec_type():
    assert parse_elf(elf(2))["type"] == "EXEC"
    assert is_executable(elf(2))
    assert not is_pie(elf(2))


def test_dyn_is_pie():
    assert parse_elf(elf(3))["type"] == "DYN"
    assert is_pie(elf(3))
    assert is_executable(elf(3))


def test_object_file_is_not_executable():
    assert not is_executable(elf(1))
