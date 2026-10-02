import struct
from png_data import SAMPLE_PNG


def parse_chunks(data):
    pass


def dimensions(data):
    pass


def text_metadata(data):
    pass


if __name__ == "__main__":
    print("size:", dimensions(SAMPLE_PNG))
    print("metadata:", text_metadata(SAMPLE_PNG))
