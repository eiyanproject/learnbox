import argparse
import json
import sys
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="A tiny to-do list.")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
