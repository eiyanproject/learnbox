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


def test_the_veth_pair_exists():
    result = run("ip -j link show veth0")
    assert result.ok, f"veth0 does not exist:\n{result.stderr}"
    result = run("ip -j link show veth1")
    assert result.ok, "veth1 does not exist - a veth is created as a pair"


def test_veth0_has_the_right_address():
    assert "10.1.1.1/24" in ns.addrs(SCRIPT, "veth0"), "veth0 should have 10.1.1.1/24"


def test_veth1_has_the_right_address():
    assert "10.1.1.2/24" in ns.addrs(SCRIPT, "veth1"), "veth1 should have 10.1.1.2/24"


def test_both_ends_are_up():
    result = run("ip -j link show veth0")
    assert "UP" in result.json()[0]["flags"], "veth0 is still down - 'ip link set veth0 up'"
    result = run("ip -j link show veth1")
    assert "UP" in result.json()[0]["flags"], "veth1 is still down - both ends need bringing up"


@pytest.mark.skipif(not ns.capabilities()["ping"], reason="ICMP is not permitted here")
def test_the_two_ends_can_actually_ping():
    """Real ICMP through the kernel, not a simulated path."""
    result = run('ping -c1 -W2 10.1.1.2 >/dev/null 2>&1 && echo REACHABLE || echo UNREACHABLE')
    assert "REACHABLE" in result.stdout, (
        "the addresses are set but the ping failed - are both ends up?"
    )
