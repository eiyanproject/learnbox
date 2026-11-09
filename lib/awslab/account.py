"""A throwaway AWS account for grading: an emulator, a script run against it,
and clients to inspect what the script built."""

from __future__ import annotations

import contextlib
import os
import socket
import subprocess
from dataclasses import dataclass, field
from typing import Any, Iterator

from ._venv import sandbox_env, use_venv

# How long a learner's script may take. The CLI starts a Python process per
# command, about half a second each, so this is generous for any lesson.
SCRIPT_TIMEOUT = 90


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@dataclass
class Account:
    """The emulator a script ran against, and how the run went."""

    endpoint: str
    region: str
    returncode: int = 0
    output: str = ""
    _clients: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def failure(self, lines: int = 20) -> str:
        """The end of the script's output, for a failed run's message."""
        tail = self.output.rstrip().splitlines()[-lines:]
        errors = [l for l in self.output.splitlines() if "An error occurred" in l or "error:" in l.lower()]
        head = f"the script stopped with exit status {self.returncode}"
        if errors:
            head += f"; the first AWS error was:\n    {errors[0].strip()}"
        return head + "\n\nlast lines of output:\n" + "\n".join("    " + l for l in tail)

    def errors(self) -> list[str]:
        """Every AWS error the script printed, even if it carried on."""
        return [l.strip() for l in self.output.splitlines() if "An error occurred" in l]

    def client(self, service: str, region: str | None = None) -> Any:
        """A boto3 client for the emulator, as the script's account."""
        key = f"{service}@{region or self.region}"
        if key not in self._clients:
            import boto3

            self._clients[key] = boto3.client(
                service,
                endpoint_url=self.endpoint,
                region_name=region or self.region,
                aws_access_key_id="testing",
                aws_secret_access_key="testing",
                aws_session_token="testing",
            )
        return self._clients[key]

    # ---- small conveniences the lessons use often ----

    def bucket_names(self) -> list[str]:
        return [b["Name"] for b in self.client("s3").list_buckets().get("Buckets", [])]

    def tags(self, items: list[dict] | None) -> dict[str, str]:
        """A resource's Tags list as a dict."""
        return {t["Key"]: t["Value"] for t in items or []}

    def by_name(self, resources: list[dict]) -> dict[str, dict]:
        """EC2-style resources keyed by their Name tag."""
        out = {}
        for r in resources:
            name = self.tags(r.get("Tags")).get("Name")
            if name:
                out[name] = r
        return out


def _run_script(script: str, env: dict[str, str]) -> tuple[int, str]:
    if not os.path.exists(script):
        return 127, f"{script} not found"
    try:
        p = subprocess.run(
            ["bash", script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=SCRIPT_TIMEOUT,
        )
    except subprocess.TimeoutExpired as e:
        out = e.output if isinstance(e.output, str) else (e.output or b"").decode(errors="replace")
        return 124, out + f"\n(stopped after {SCRIPT_TIMEOUT} seconds)"
    return p.returncode, p.stdout


@contextlib.contextmanager
def lab(script: str | None = "setup.sh", region: str = "us-east-1") -> Iterator[Account]:
    """A fresh emulator for the length of the block, with script run against it.

    The script runs under bash, from the current directory, with the
    environment pointing every `aws` command at the emulator. Pass None to get
    an empty account and drive it from the test.
    """
    use_venv()
    from moto.server import ThreadedMotoServer

    port = free_port()
    server = ThreadedMotoServer(ip_address="127.0.0.1", port=port, verbose=False)
    server.start()
    endpoint = f"http://127.0.0.1:{port}"
    try:
        # moto keeps its accounts in module state; a second lab in the same
        # test process must not see the first one's leftovers.
        import urllib.request

        urllib.request.urlopen(urllib.request.Request(endpoint + "/moto-api/reset", method="POST"), timeout=10).read()
        acct = Account(endpoint=endpoint, region=region)
        if script is not None:
            env = sandbox_env(endpoint)
            env["AWS_DEFAULT_REGION"] = region
            acct.returncode, acct.output = _run_script(script, env)
        yield acct
    finally:
        server.stop()

