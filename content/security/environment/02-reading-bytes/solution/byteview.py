def hexdump(data):
    # Sixteen bytes to a line. The offset says where in the data each line
    # starts, which is how you refer to "the byte at 0x10" when reading output.
    lines = []
    for offset in range(0, len(data), 16):
        chunk = data[offset:offset + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{offset:08x}: {hex_part}  {ascii_part}")
    return "\n".join(lines)


def find_strings(data, min_len=4):
    # This is the whole of what `strings` does: collect printable runs, and
    # keep the ones long enough to be deliberate rather than coincidence.
    found = []
    run = []
    for b in data:
        if 32 <= b <= 126:
            run.append(chr(b))
        else:
            if len(run) >= min_len:
                found.append("".join(run))
            run = []
    if len(run) >= min_len:
        found.append("".join(run))
    return found


if __name__ == "__main__":
    print(hexdump(b"\x7fELF\x02\x01hello"))
    print(find_strings(b"\x00\x01password\x00\xffok\x00"))
