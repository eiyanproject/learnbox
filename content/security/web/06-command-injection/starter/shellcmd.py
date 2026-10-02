import os
import subprocess


def run_vulnerable(host):
    # VULNERABLE: host is pasted into a shell command string.
    return os.popen("echo pinging " + host).read()


def injection_payload():
    # Return a host value that smuggles in a second command (output contains 42).
    pass


def run_safe(host):
    # Run the ping with no shell, so metacharacters are inert.
    pass


if __name__ == "__main__":
    p = injection_payload()
    print("vulnerable:", run_vulnerable(p).strip())
    print("safe:      ", run_safe(p).strip())
