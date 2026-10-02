import base64
import struct
from capture_data import SAMPLE


def parse_pcap(data):
    pass


def frame_endpoints(frame):
    pass


def frame_payload(frame):
    pass


def find_basic_auth(frames):
    pass


if __name__ == "__main__":
    frames = parse_pcap(SAMPLE)
    print(len(frames), "packets")
    for f in frames:
        print(frame_endpoints(f))
    print("credentials in the clear:", find_basic_auth(frames))
