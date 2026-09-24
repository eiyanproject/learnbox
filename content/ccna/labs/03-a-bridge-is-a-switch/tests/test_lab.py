import pathlib

import pytest

from netlab import ns

pytestmark = pytest.mark.skipif(
    not ns.available() or not ns.capabilities()["bridge"],
    reason="unprivileged network namespaces with bridges are unavailable here",
)

SCRIPT = pathlib.Path("lab.sh").read_text(encoding="utf-8")


def run(extra=""):
    return ns.run(SCRIPT + "\n" + extra)


def test_the_script_runs_without_errors():
    result = run()
    assert result.ok, f"lab.sh failed:\n{result.stderr}"


def test_the_bridge_exists_and_is_up():
    result = run("ip -j link show br0")
    assert result.ok, f"no bridge called br0:\n{result.stderr}"
    assert "UP" in result.json()[0]["flags"], "br0 is down - a bridge that is down forwards nothing"


def test_all_three_hosts_are_addressed():
    for n in (1, 2, 3):
        found = ns.addrs(SCRIPT, f"h{n}")
        assert f"10.0.0.{n}/24" in found, f"h{n} should have 10.0.0.{n}/24, has {found}"


def test_all_three_ports_are_in_the_bridge():
    result = run("bridge link")
    for n in (1, 2, 3):
        assert f"h{n}br" in result.stdout, f"h{n}br is not attached to the bridge (master br0)"


def test_the_switch_ports_have_no_addresses():
    """A switch port does not have an IP; the host end does."""
    for n in (1, 2, 3):
        assert ns.addrs(SCRIPT, f"h{n}br") == [], (
            f"h{n}br should have no address - it is a switch port"
        )


@pytest.mark.skipif(not ns.capabilities()["ping"], reason="ICMP is not permitted here")
def test_every_host_reaches_every_other():
    result = run(
        'for a in 1 2 3; do ping -c1 -W2 10.0.0.$a >/dev/null 2>&1 '
        '&& echo "OK$a" || echo "FAIL$a"; done'
    )
    for n in (1, 2, 3):
        assert f"OK{n}" in result.stdout, f"10.0.0.{n} was not reachable through the bridge"


@pytest.mark.skipif(not ns.capabilities()["ping"], reason="ICMP is not permitted here")
def test_no_routing_is_involved():
    """One broadcast domain: the only route is the connected subnet."""
    result = run("ping -c1 -W2 10.0.0.2 >/dev/null 2>&1; ip route")
    assert "default" not in result.stdout, (
        "there should be no default route - the hosts reach each other at layer 2"
    )
