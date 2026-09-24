"""Run me: python run.py - builds the lab and reports on it."""
import pathlib

from netlab import ns

if not ns.available():
    raise SystemExit("network namespaces are not available on this machine")

script = pathlib.Path("lab.sh").read_text(encoding="utf-8")
result = ns.run(
    script
    + """
echo "--- this namespace"
ip -br addr
echo "--- the peer namespace"
nsenter -t "$peer" -n ip -br addr 2>/dev/null || echo "  (no peer pid in \$peer)"
echo "--- ping across the cable"
ping -c1 -W1 10.1.1.2 >/dev/null 2>&1 && echo "10.1.1.2 reachable" || echo "10.1.1.2 UNREACHABLE"
"""
)
print(result.stdout, end="")
if result.stderr.strip():
    print("--- errors")
    print(result.stderr, end="")
raise SystemExit(0 if result.ok else 1)
