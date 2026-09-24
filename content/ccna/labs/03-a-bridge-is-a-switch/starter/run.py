"""Run me: python run.py - builds the lab and reports on it."""
import pathlib

from netlab import ns

if not ns.available():
    raise SystemExit("network namespaces are not available on this machine")

script = pathlib.Path("lab.sh").read_text(encoding="utf-8")
result = ns.run(
    script
    + """
echo "--- bridge ports"
bridge link 2>/dev/null || echo "  (no bridge)"
echo "--- addresses"
ip -br addr
echo "--- reachability"
for a in 1 2 3; do
  ping -c1 -W1 "10.0.0.$a" >/dev/null 2>&1 && echo "  10.0.0.$a reachable" || echo "  10.0.0.$a UNREACHABLE"
done
echo "--- learned MAC addresses"
bridge fdb show br br0 2>/dev/null | head -6
"""
)
print(result.stdout, end="")
if result.stderr.strip():
    print("--- errors")
    print(result.stderr, end="")
raise SystemExit(0 if result.ok else 1)
