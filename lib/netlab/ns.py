"""Real Linux network namespaces, for the labs that sit beside the simulator.

The simulator teaches Cisco syntax; this teaches what the kernel actually does.
Same concepts, real packets: `ip link`, `ip addr`, veth pairs, bridges, and a
ping that is genuine ICMP rather than a graph walk.

Everything runs inside `unshare -Urn`: a user namespace where the learner is
root, plus a network namespace of its own. Nothing here needs real privileges
and nothing can touch the container's own networking - the namespace disappears
when the process exits.

What is available varies by kernel and container configuration, so `capabilities()`
probes rather than assumes, and the lessons only assert what a probe confirms.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap

__all__ = ["run", "capabilities", "available", "NSResult", "addrs", "NetnsUnavailable"]

PRELUDE = """
set -e
ip link set lo up 2>/dev/null || true
"""

# A lab that parks a sleeping process in a second namespace leaves it holding
# our stdout, so reading the pipe would block until that sleep expires however
# long ago the script finished. Killing the jobs at the end closes the fd and
# tears the extra namespaces down at the same time.
EPILOGUE = """
kill $(jobs -p) 2>/dev/null || true
wait 2>/dev/null || true
"""


class NetnsUnavailable(RuntimeError):
    """The kernel or container refuses unprivileged network namespaces."""


class NSResult:
    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def json(self) -> object:
        """Parse `ip -j` output from the last line that looks like JSON."""
        for line in reversed(self.stdout.splitlines()):
            line = line.strip()
            if line.startswith(("[", "{")):
                return json.loads(line)
        raise ValueError(f"no JSON in output:\n{self.stdout}\n{self.stderr}")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<NSResult rc={self.returncode} out={self.stdout[:80]!r}>"


def run(script: str, timeout: int = 20, check: bool = False) -> NSResult:
    """
    Run a shell script inside a fresh user+network namespace.

    The script starts with lo up, because a namespace's loopback arrives down
    and almost nothing behaves sensibly until it is up - a good first surprise
    for a learner, and a bad one to leave in every test.
    """
    if not available():
        raise NetnsUnavailable(
            "unprivileged network namespaces are not available here "
            "(needs a kernel allowing unprivileged userns, and a container with nesting)"
        )
    proc = subprocess.run(
        ["unshare", "-Urn", "bash", "-c", PRELUDE + textwrap.dedent(script) + EPILOGUE],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    result = NSResult(proc.returncode, proc.stdout, proc.stderr)
    if check and not result.ok:
        raise RuntimeError(f"namespace script failed:\n{result.stderr}")
    return result


_cache: dict[str, bool] | None = None


def capabilities() -> dict[str, bool]:
    """
    What this machine actually allows. Probed once and remembered.

    Lessons use this to skip rather than fail: a lab that cannot run because
    the kernel forbids it is not a wrong answer from the learner.
    """
    global _cache
    if _cache is not None:
        return _cache
    caps = {"netns": False, "veth": False, "ping": False, "bridge": False, "forwarding": False}
    if shutil.which("unshare") and shutil.which("ip"):
        try:
            probe = subprocess.run(
                ["unshare", "-Urn", "bash", "-c", "ip link add v0 type veth peer name v1 && echo VETH"],
                capture_output=True, text=True, timeout=15,
            )
            caps["netns"] = probe.returncode == 0
            caps["veth"] = "VETH" in probe.stdout
        except (OSError, subprocess.SubprocessError):
            return _set_cache(caps)
    if not caps["netns"]:
        return _set_cache(caps)

    checks = {
        "ping": "ip link add v0 type veth peer name v1; ip addr add 10.255.0.1/24 dev v0; "
                "ip addr add 10.255.0.2/24 dev v1; ip link set v0 up; ip link set v1 up; "
                "ping -c1 -W1 10.255.0.2 >/dev/null && echo YES",
        "bridge": "ip link add br0 type bridge && echo YES",
        "forwarding": "echo 1 > /proc/sys/net/ipv4/ip_forward && echo YES",
    }
    for name, script in checks.items():
        try:
            out = run(script, timeout=15)
            caps[name] = "YES" in out.stdout
        except Exception:
            caps[name] = False
    return _set_cache(caps)


def _set_cache(caps: dict[str, bool]) -> dict[str, bool]:
    global _cache
    _cache = caps
    return caps


def available() -> bool:
    if _cache is not None:
        return _cache["netns"]
    if not (shutil.which("unshare") and shutil.which("ip")):
        return False
    try:
        probe = subprocess.run(
            ["unshare", "-Urn", "true"], capture_output=True, text=True, timeout=15
        )
        return probe.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def addrs(script: str, interface: str) -> list[str]:
    """Run a script, then report the addresses on one interface inside it."""
    out = run(script + f"\nip -j addr show {interface}\n")
    data = out.json()
    if not data:
        return []
    return [
        f"{a['local']}/{a['prefixlen']}"
        for a in data[0].get("addr_info", [])
        if a.get("family") == "inet"
    ]
