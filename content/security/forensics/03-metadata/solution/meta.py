import struct
from png_data import SAMPLE_PNG


def parse_chunks(data):
    # Walk from just past the 8-byte signature: read a length and type, take
    # the data, skip the 4-byte CRC, repeat.
    chunks = []
    offset = 8
    while offset + 8 <= len(data):
        length = struct.unpack("!I", data[offset:offset + 4])[0]
        ctype = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        chunks.append((ctype.decode("latin1"), body))
        offset += 8 + length + 4   # header + data + CRC
    return chunks


def dimensions(data):
    for ctype, body in parse_chunks(data):
        if ctype == "IHDR":
            width, height = struct.unpack("!II", body[:8])
            return (width, height)
    return None


def text_metadata(data):
    # tEXt data is keyword\x00value - the file quietly labelling itself.
    meta = {}
    for ctype, body in parse_chunks(data):
        if ctype == "tEXt":
            key, _, value = body.partition(b"\x00")
            meta[key.decode("latin1")] = value.decode("latin1")
    return meta


if __name__ == "__main__":
    print("size:", dimensions(SAMPLE_PNG))
    print("metadata:", text_metadata(SAMPLE_PNG))
