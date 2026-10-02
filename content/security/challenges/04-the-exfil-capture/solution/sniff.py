import struct
from data import EXFIL


def _frames(data):
    frames, off = [], 24
    while off + 16 <= len(data):
        incl = struct.unpack("<IIII", data[off:off + 16])[2]
        off += 16
        frames.append(data[off:off + incl])
        off += incl
    return frames


def _payload(frame):
    ihl = (frame[14] & 0x0F) * 4
    tcp = 14 + ihl
    data_off = (frame[tcp + 12] >> 4) * 4
    return frame[tcp + data_off:]


def find_exfil(pcap):
    for frame in _frames(pcap):
        payload = _payload(frame)
        if b"secret=" in payload:
            field = payload.split(b"secret=", 1)[1].split(b"&", 1)[0]
            return field.decode()
    return None


if __name__ == "__main__":
    print("exfiltrated:", find_exfil(EXFIL))
