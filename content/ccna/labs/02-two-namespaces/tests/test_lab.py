import pathlib

import pytest

from netlab import ns

pytestmark = pytest.mark.skipif(
    not ns.available(),
    reason="unprivileged network namespaces are unavailable here (the container needs nesting)",
)

SCRIPT = pathlib.Path("lab.sh").read_text(encoding="utf-8")


def run(extra=""):
    return ns.run(SCRIPT + "\n" + extra)


def test_the_script_runs_without_errors():
    result = run()
    assert result.ok, f"lab.sh failed:\n{result.stderr}"


def test_veth0_stayed_here_and_is_addressed():
    assert "10.1.1.1/24" in ns.addrs(SCRIPT, "veth0"), "veth0 should have 10.1.1.1/24"


def test_veth1_is_no_longer_in_this_namespace():
    """Moving an interface removes it from here entirely."""
    result = run("ip link show veth1 2>/dev/null && echo STILL_HERE || echo MOVED")
    assert "MOVED" in result.stdout, (
        "veth1 is still in this namespace - it was never moved to the peer"
    )


def test_the_peer_pid_was_captured():
    result = run('test -n "$peer" && echo HAVE_PEER || echo NO_PEER')
    assert "HAVE_PEER" in result.stdout, "leave the peer namespace's pid in a variable called 'peer'"


def test_the_peer_has_veth1_addressed():
    result = run('nsenter -t "$peer" -n ip -j addr show veth1')
    assert result.ok, f"veth1 is not in the peer namespace:\n{result.stderr}"
    addresses = [
        f"{a['local']}/{a['prefixlen']}"
        for a in result.json()[0].get("addr_info", [])
        if a.get("family") == "inet"
    ]
    assert "10.1.1.2/24" in addresses, f"veth1 should have 10.1.1.2/24, has {addresses}"


def test_the_far_end_is_up():
    result = run('nsenter -t "$peer" -n ip -j link show veth1')
    assert "UP" in result.json()[0]["flags"], (
        "veth1 is down inside the peer - it needs bringing up there, not here"
    )


@pytest.mark.skipif(not ns.capabilities()["ping"], reason="ICMP is not permitted here")
def test_the_ping_crosses_the_namespace_boundary():
    result = run('ping -c1 -W2 10.1.1.2 >/dev/null 2>&1 && echo REACHABLE || echo UNREACHABLE')
    assert "REACHABLE" in result.stdout, "the ping across the veth failed"
