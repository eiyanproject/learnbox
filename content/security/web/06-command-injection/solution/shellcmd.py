import os
import subprocess


def run_vulnerable(host):
    # VULNERABLE: host is pasted into a shell command string.
    return os.popen("echo pinging " + host).read()


def injection_payload():
    # The ; ends the echo and starts a second command. expr computes 42, a
    # value that appears nowhere in the input - so seeing it proves execution.
    return r"127.0.0.1; expr 6 \* 7"


def run_safe(host):
    # A list, not a string: subprocess runs echo with host as one literal
    # argument. No shell means no metacharacters, so nothing can be injected.
    return subprocess.run(
        ["echo", "pinging", host], capture_output=True, text=True
    ).stdout


if __name__ == "__main__":
    p = injection_payload()
    print("vulnerable:", run_vulnerable(p).strip())
    print("safe:      ", run_safe(p).strip())
