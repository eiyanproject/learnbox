import struct
from data import EXFIL


def find_exfil(pcap):
    # Walk the frames, find the HTTP payload, read the secret= form field.
    pass


if __name__ == "__main__":
    print("exfiltrated:", find_exfil(EXFIL))
