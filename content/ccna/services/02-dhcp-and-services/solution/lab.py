"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("one-router", {"R1": "r1.ios"}, [("PC1", "R1")])
)
