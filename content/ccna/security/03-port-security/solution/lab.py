"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("switched", {"SW1": "sw1.ios"}, [("PC1", "PC2")])
)
