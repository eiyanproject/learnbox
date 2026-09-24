"""Run me: python run.py - builds the lab and reports on it."""
import pathlib

from netlab import ns

if not ns.available():
    raise SystemExit("network namespaces are not available on this machine")

script = pathlib.Path("lab.sh").read_text(encoding="utf-8")
result = ns.run(
    script
    + """
echo "--- interfaces"
ip -br addr
echo "--- ping"
ping -c1 -W1 10.1.1.2 >/dev/null 2>&1 && echo "10.1.1.2 reachable" || echo "10.1.1.2 UNREACHABLE"
"""
)
print(result.stdout, end="")
if result.stderr.strip():
    print("--- errors")
    print(result.stderr, end="")
raise SystemExit(0 if result.ok else 1)
