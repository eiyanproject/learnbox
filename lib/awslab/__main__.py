"""Command line: the sandbox account behind the terminal's `aws` command.

    aws ...                 (the wrapper) the real AWS CLI, against the sandbox
    awslab run setup.sh     empty the sandbox, then run a lesson's script in it
    awslab reset            empty the sandbox
    awslab status           is the sandbox running, and where
    awslab stop             stop it (the next `aws` starts it again)
    awslab env              shell exports that point boto3 or the CLI at it
    awslab given [name]     build a ready-made setup a lesson builds on and
                            print its IDs:  eval "$(awslab given vpc)"
    awslab given name --show   the same setup as the CLI commands it stands for

The sandbox is a moto emulator listening on 127.0.0.1 only, started on first
use and left running. Everything in it lives in memory: stopping it, or a
reset, gives you a new empty account.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request

from ._venv import DEFAULT_REGION, EMULATOR_ENV, sandbox_env, venv_bin

PORT = int(os.environ.get("LEARNBOX_AWS_PORT", "4599"))
ENDPOINT = f"http://127.0.0.1:{PORT}"
STATE = os.path.join(os.path.expanduser("~"), ".cache", "awslab")
PIDFILE = os.path.join(STATE, "moto.pid")
LOGFILE = os.path.join(STATE, "moto.log")


def listening() -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def start() -> None:
    if listening():
        return
    os.makedirs(STATE, exist_ok=True)
    with open(LOGFILE, "ab") as log:
        p = subprocess.Popen(
            [venv_bin("python"), "-m", "moto.server", "-H", "127.0.0.1", "-p", str(PORT)],
            env={**os.environ, **EMULATOR_ENV},
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,  # outlives the shell that started it
        )
    with open(PIDFILE, "w") as f:
        f.write(str(p.pid))
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if listening():
            return
        if p.poll() is not None:
            break
        time.sleep(0.2)
    sys.exit(f"awslab: the sandbox did not start; see {LOGFILE}")


def reset() -> None:
    req = urllib.request.Request(ENDPOINT + "/moto-api/reset", method="POST")
    urllib.request.urlopen(req, timeout=10).read()


def with_endpoint(args: list[str], endpoint: str) -> list[str]:
    """The arguments with --endpoint-url added, unless the learner gave one.

    The environment variable alone is not enough: CLI v1 overrides it for a
    few services (SQS, RDS among them) with their legacy public endpoints,
    which would send those calls to the real AWS. The command-line option
    wins over everything.
    """
    if any(a == "--endpoint-url" or a.startswith("--endpoint-url=") for a in args):
        return args
    return ["--endpoint-url", endpoint, *args]


def cmd_aws(args: list[str]) -> int:
    aws = venv_bin("aws")
    if "AWS_ENDPOINT_URL" in os.environ:
        # Already pointed somewhere - a lesson's check, running its own
        # throwaway emulator.
        os.execv(aws, [aws, *with_endpoint(args, os.environ["AWS_ENDPOINT_URL"])])
    start()
    os.execve(aws, [aws, *with_endpoint(args, ENDPOINT)], sandbox_env(ENDPOINT))
    return 0  # not reached


def cmd_run(args: list[str]) -> int:
    if len(args) != 1:
        print("usage: awslab run <script>", file=sys.stderr)
        return 2
    start()
    reset()
    print(f"awslab: empty sandbox account, region {DEFAULT_REGION}; running {args[0]}\n", flush=True)
    env = sandbox_env(ENDPOINT)
    env["PS4"] = "$ "  # show each command as it would be typed
    rc = subprocess.call(["bash", "-x", args[0]], env=env)
    print(f"\nawslab: {args[0]} exited {rc}. What it built is still there - look around with aws, or `awslab reset` to clear it.")
    return rc


def cmd_stop() -> int:
    try:
        with open(PIDFILE) as f:
            os.killpg(int(f.read().strip()), signal.SIGTERM)
    except (OSError, ValueError):
        pass
    for _ in range(25):  # it takes a moment to let go of the port
        if not listening():
            break
        time.sleep(0.2)
    print("awslab: stopped" if not listening() else "awslab: still running (started elsewhere?)")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "aws":
        return cmd_aws(rest)
    if cmd == "run":
        return cmd_run(rest)
    if cmd == "reset":
        start()
        reset()
        print("awslab: the sandbox account is empty again")
        return 0
    if cmd == "status":
        print(f"awslab: {'running' if listening() else 'not running'} at {ENDPOINT}, region {DEFAULT_REGION}")
        return 0
    if cmd == "stop":
        return cmd_stop()
    if cmd == "given":
        from . import given

        if not rest:
            print("awslab given: " + ", ".join(given.names()))
            return 0
        if rest[0] not in given.names():
            print(f"awslab given: no {rest[0]!r}; there is {', '.join(given.names())}", file=sys.stderr)
            return 2
        if "--show" in rest:
            sys.stdout.write(given.show(rest[0]))
            return 0
        endpoint = os.environ.get("AWS_ENDPOINT_URL")
        if not endpoint:
            start()
            endpoint = ENDPOINT
        region = os.environ.get("AWS_DEFAULT_REGION", DEFAULT_REGION)
        sys.stdout.write(given.build(rest[0], endpoint, region))
        return 0
    if cmd == "env":
        start()
        for k, v in sandbox_env(ENDPOINT, base={}).items():
            print(f"export {k}={v!r}" if v else f"export {k}=")
        return 0
    print(f"awslab: unknown command {cmd!r}; try awslab help", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
