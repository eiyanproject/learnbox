"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("l3-switch", {"SW1": "sw1.ios"}, [("PC1", "PC2"), ("PC1", "PC3"), ("PC2", "10.0.20.1")])
)
