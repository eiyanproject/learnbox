"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("two-routers", {"R1": "r1.ios", "R2": "r2.ios"}, [("PC1", "PC2"), ("PC2", "PC1")])
)
