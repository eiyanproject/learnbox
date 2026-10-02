import base64
import struct
from capture_data import SAMPLE


def parse_pcap(data):
    # Skip the 24-byte global header, then walk record by record: a 16-byte
    # record header whose third field is the captured length, then the frame.
    frames = []
    offset = 24
    while offset + 16 <= len(data):
        _, _, incl_len, _ = struct.unpack("<IIII", data[offset:offset + 16])
        offset += 16
        frames.append(data[offset:offset + incl_len])
        offset += incl_len
    return frames


def _tcp_start(frame):
    ihl = (frame[14] & 0x0F) * 4      # IP header length, in bytes
    return 14 + ihl                    # Ethernet(14) + IP


def frame_endpoints(frame):
    src_ip = ".".join(str(b) for b in frame[26:30])
    dst_ip = ".".join(str(b) for b in frame[30:34])
    tcp = _tcp_start(frame)
    src_port = int.from_bytes(frame[tcp:tcp + 2], "big")
    dst_port = int.from_bytes(frame[tcp + 2:tcp + 4], "big")
    return (src_ip, dst_ip, src_port, dst_port)


def frame_payload(frame):
    tcp = _tcp_start(frame)
    data_off = (frame[tcp + 12] >> 4) * 4     # TCP header length, in bytes
    return frame[tcp + data_off:]


def find_basic_auth(frames):
    marker = b"Authorization: Basic "
    for frame in frames:
        payload = frame_payload(frame)
        if marker in payload:
            token = payload.split(marker, 1)[1].split(b"\r\n", 1)[0]
            # base64 is an encoding, not encryption: the creds decode directly.
            return base64.b64decode(token).decode()
    return None


if __name__ == "__main__":
    frames = parse_pcap(SAMPLE)
    print(len(frames), "packets")
    for f in frames:
        print(frame_endpoints(f))
    print("credentials in the clear:", find_basic_auth(frames))
